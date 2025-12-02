import curses
import time
from typing import List

from utils.ui_helpers import init_colors, draw_content_window, draw_section_header
from utils.input_helpers import handle_input, GLOBAL_KEYS
from process import populate_process_list
from process_struct import ProcessInfo

# Fixed column widths
COL_WIDTHS = {
    "user": 16,
    "pid": 6,
    "cpu": 6,
    "mem": 6,
    "vsz": 10,
    "rss": 10,
    "tty": 8,
    "stat": 6,
    "start": 8,
    "time": 10,
    "command": 0,  # dynamic width
}

SORT_KEYS = {
    "cpu": "cpu_percent",
    "mem": "mem_percent",
    "pid": "pid",
    "name": "command",
}


def get_all_processes(sort_mode: str = "cpu") -> List[ProcessInfo]:
    processes = populate_process_list()
    sort_attr = SORT_KEYS.get(sort_mode, "cpu_percent")
    reverse = sort_attr in ("cpu_percent", "mem_percent")
    processes.sort(key=lambda p: getattr(p, sort_attr, 0), reverse=reverse)
    return processes


def draw_process_list(
    win: curses.window,
    processes: List[ProcessInfo],
    selected_index: int,
    start: int,
    sort_mode: str,
) -> None:
    """Render a scrollable list of processes with fixed column widths."""
    height, width = win.getmaxyx()
    draw_section_header(win, 1, f"Running Processes (Sort by {sort_mode.upper()})")

    header_fmt = (
        f"{{user:<{COL_WIDTHS['user']}}} {{pid:<{COL_WIDTHS['pid']}}} "
        f"{{cpu:>{COL_WIDTHS['cpu']}}} {{mem:>{COL_WIDTHS['mem']}}} "
        f"{{vsz:>{COL_WIDTHS['vsz']}}} {{rss:>{COL_WIDTHS['rss']}}} "
        f"{{tty:<{COL_WIDTHS['tty']}}} {{stat:<{COL_WIDTHS['stat']}}} "
        f"{{start:<{COL_WIDTHS['start']}}} {{time:<{COL_WIDTHS['time']}}} COMMAND"
    )
    win.addstr(
        2,
        2,
        header_fmt.format(
            user="USER",
            pid="PID",
            cpu="%CPU",
            mem="%MEM",
            vsz="VSZ",
            rss="RSS",
            tty="TTY",
            stat="STAT",
            start="START",
            time="TIME",
        ),
    )
    win.hline(3, 2, curses.ACS_HLINE, width - 4)

    visible_lines = height - 6
    end = min(start + visible_lines, len(processes))

    for i, proc in enumerate(processes[start:end], start=start):
        y = 4 + (i - start)
        is_selected = i == selected_index

        tty_display = (proc.tty or "?")[: COL_WIDTHS["tty"] - 1]
        used_width = sum(COL_WIDTHS.values())
        command_width = max(10, width - 4 - used_width)
        command_display = (proc.command or "")[:command_width]

        line = (
            f"{proc.user:<{COL_WIDTHS['user']}} "
            f"{proc.pid:<{COL_WIDTHS['pid']}} "
            f"{proc.cpu_percent:>{COL_WIDTHS['cpu']}.1f} "
            f"{proc.mem_percent:>{COL_WIDTHS['mem']}.1f} "
            f"{proc.vsz:>{COL_WIDTHS['vsz']}} "
            f"{proc.rss:>{COL_WIDTHS['rss']}} "
            f"{tty_display:<{COL_WIDTHS['tty']}} "
            f"{proc.stat:<{COL_WIDTHS['stat']}} "
            f"{proc.start:<{COL_WIDTHS['start']}} "
            f"{proc.time:<{COL_WIDTHS['time']}} "
            f"{command_display}"
        )

        color_pair = 6 if is_selected else 5
        win.attron(curses.color_pair(color_pair))
        win.addstr(y, 2, line[:width])
        win.attroff(curses.color_pair(color_pair))

    # Footer
    win.attron(curses.color_pair(2))
    win.addstr(height - 2, 2, "[↑/↓] Move   [C]PU  [M]em  [P]ID  [N]ame  [K]ill")
    win.attroff(curses.color_pair(2))


def render_processes(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """Interactive process viewer, relies on curses.wrapper for safe cleanup."""
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    selected_index = 0
    scroll_start = 0
    sort_mode = "cpu"
    refresh_interval = 1.0
    last_refresh = 0.0
    cached_processes: list[ProcessInfo] = []
    needs_refresh = True

    while True:
        content_win = draw_content_window(
            stdscr,
            title="Process Manager",
            nav_items=nav_items,
            active_page=active_page,
        )

        if content_win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.1)
            continue

        now = time.time()
        if (
            needs_refresh
            or (now - last_refresh) >= refresh_interval
            or not cached_processes
        ):
            cached_processes = get_all_processes(sort_mode)
            last_refresh = now
            needs_refresh = False

        processes = cached_processes
        if not processes:
            content_win.addstr(2, 2, "No processes found.")
            content_win.refresh()
            time.sleep(0.5)
            continue

        # Clamp selected_index before drawing
        selected_index = max(0, min(selected_index, len(processes) - 1))

        # Adjust scrolling
        height, _ = content_win.getmaxyx()
        visible_lines = height - 6
        if selected_index < scroll_start:
            scroll_start = selected_index
        elif selected_index >= scroll_start + visible_lines:
            scroll_start = selected_index - visible_lines + 1

        draw_process_list(
            content_win, processes, selected_index, scroll_start, sort_mode
        )

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        # Handle input
        key = stdscr.getch()
        if key == -1:
            time.sleep(0.1)
            continue
        # Navigation
        if key == curses.KEY_UP:
            selected_index -= 1
            selected_index = max(0, selected_index)  # clamp
        elif key == curses.KEY_DOWN:
            selected_index += 1
            selected_index = min(selected_index, len(processes) - 1)

        # Sorting (separate if statements, not elif)
        if key in (ord("c"), ord("C")):
            sort_mode = "cpu"
            needs_refresh = True
        elif key in (ord("m"), ord("M")):
            sort_mode = "mem"
            needs_refresh = True
        elif key in (ord("p"), ord("P")):
            sort_mode = "pid"
            needs_refresh = True
        elif key in (ord("n"), ord("N")):
            sort_mode = "name"
            needs_refresh = True

        # Kill selected process
        elif key in (ord("k"), ord("K")):
            try:
                import os

                os.kill(processes[selected_index].pid, 9)
                needs_refresh = True
            except (PermissionError, ProcessLookupError):
                pass

        # Quit or switch pages
        elif key in (
            ord("d"),
            ord("D"),
            ord("1"),
            ord("3"),
            ord("4"),
            ord("5"),
            ord("q"),
            ord("Q"),
        ):
            return key

        time.sleep(0.1)
