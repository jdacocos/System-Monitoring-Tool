"""
pages/process_page.py

Provides an interactive process manager UI using curses.

Displays a scrollable list of processes with CPU, memory, VSZ, RSS, TTY,
STAT, start time, elapsed time, and command.

Features:
- Sorting by CPU, memory, PID, or name
- Navigation with arrow keys
- Kill a process
- Refresh interval handling
"""

import curses
import os
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
    """Return all processes sorted by the given sort_mode."""
    processes = populate_process_list()
    sort_attr = SORT_KEYS.get(sort_mode, "cpu_percent")
    reverse = sort_attr in ("cpu_percent", "mem_percent")
    processes.sort(key=lambda p: getattr(p, sort_attr, 0), reverse=reverse)
    return processes


def draw_process_row(
    win: curses.window, y: int, proc: ProcessInfo, width: int, is_selected: bool
):
    """Draw a single process row in the window."""
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


def draw_process_list(
    win: curses.window,
    processes: List[ProcessInfo],
    selected_index: int,
    start: int,
    sort_mode: str,
) -> None:
    """Render scrollable process list."""
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
    for i, proc in enumerate(processes[start : start + visible_lines], start=start):
        y = 4 + (i - start)
        draw_process_row(win, y, proc, width, i == selected_index)

    draw_footer(win, height)


def handle_process_input(key: int, selected_index: int, processes: List[ProcessInfo]):
    """Handle key input for navigation, sorting, killing, and quitting."""
    new_selected = selected_index
    new_sort_mode = None
    kill_flag = False
    quit_flag = False

    # Navigation
    if key == curses.KEY_UP:
        new_selected = max(0, selected_index - 1)
    elif key == curses.KEY_DOWN:
        new_selected = min(selected_index + 1, len(processes) - 1)

    # Sorting
    if key in (ord("c"), ord("C")):
        new_sort_mode = "cpu"
    elif key in (ord("m"), ord("M")):
        new_sort_mode = "mem"
    elif key in (ord("p"), ord("P")):
        new_sort_mode = "pid"
    elif key in (ord("n"), ord("N")):
        new_sort_mode = "name"

    # Kill process
    if key in (ord("k"), ord("K")):
        kill_flag = True

    # Quit or switch pages
    if key in (
        ord("d"),
        ord("D"),
        ord("1"),
        ord("3"),
        ord("4"),
        ord("5"),
        ord("q"),
        ord("Q"),
    ):
        quit_flag = True

    return new_selected, new_sort_mode, kill_flag, quit_flag


def draw_footer(win: curses.window, height: int) -> None:
    """Draw the footer with available controls."""
    win.attron(curses.color_pair(2))
    win.addstr(height - 2, 2, "[↑/↓] Move   [C]PU  [M]em  [P]ID  [N]ame  [K]ill")
    win.attroff(curses.color_pair(2))


def update_process_cache(
    cached: list[ProcessInfo], sort_mode: str, last_refresh: float, interval: float
) -> tuple[list[ProcessInfo], float]:
    """Update process cache if needed based on refresh interval."""
    now = time.time()
    if not cached or (now - last_refresh) >= interval:
        cached = get_all_processes(sort_mode)
        last_refresh = now
    return cached, last_refresh


def adjust_scroll(selected_index: int, scroll_start: int, visible_lines: int) -> int:
    """Return new scroll_start based on selected_index and visible lines."""
    if selected_index < scroll_start:
        scroll_start = selected_index
    elif selected_index >= scroll_start + visible_lines:
        scroll_start = selected_index - visible_lines + 1
    return scroll_start


def draw_and_refresh(
    win: curses.window,
    processes: list[ProcessInfo],
    selected_index: int,
    scroll_start: int,
    sort_mode: str,
):
    """Draw process list and refresh curses windows."""
    draw_process_list(win, processes, selected_index, scroll_start, sort_mode)
    win.noutrefresh()
    curses.doupdate()


def init_process_viewer(stdscr: curses.window) -> dict:
    """Initialize curses and default state for the process viewer."""
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)
    return {
        "selected_index": 0,
        "scroll_start": 0,
        "sort_mode": "cpu",
        "refresh_interval": 1.0,
        "last_refresh": 0.0,
        "cached_processes": [],
        "needs_refresh": True,
    }


def render_processes(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """Interactive curses process viewer with sorting, scrolling, and kill."""
    state = init_process_viewer(stdscr)

    while True:
        win = draw_content_window(stdscr, "Process Manager", nav_items, active_page)
        if win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.1)
            continue

        # Refresh process list if needed
        now = time.time()
        if (
            state["needs_refresh"]
            or not state["cached_processes"]
            or (now - state["last_refresh"] >= state["refresh_interval"])
        ):
            state["cached_processes"], state["last_refresh"] = refresh_processes(
                state["cached_processes"],
                state["sort_mode"],
                state["last_refresh"],
                state["refresh_interval"],
            )
            state["needs_refresh"] = False

        processes = state["cached_processes"]
        if not processes:
            win.addstr(2, 2, "No processes found.")
            win.refresh()
            time.sleep(0.5)
            continue

        # Clamp selection and adjust scroll
        state["selected_index"] = max(
            0, min(state["selected_index"], len(processes) - 1)
        )
        height, _ = win.getmaxyx()
        state["scroll_start"] = adjust_scroll(
            state["selected_index"], state["scroll_start"], height, len(processes)
        )

        # Draw list and footer
        draw_process_list(
            win,
            processes,
            state["selected_index"],
            state["scroll_start"],
            state["sort_mode"],
        )
        win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        # Handle input
        key = stdscr.getch()
        if key != -1:
            sel, sort_mode, kill_flag, quit_flag = handle_process_input(
                key, state["selected_index"], processes
            )
            state["selected_index"] = sel
            if sort_mode:
                state["sort_mode"] = sort_mode
                state["needs_refresh"] = True
            if kill_flag:
                try:
                    os.kill(processes[state["selected_index"]].pid, 9)
                    state["needs_refresh"] = True
                except (PermissionError, ProcessLookupError):
                    pass
            if quit_flag:
                return key
        time.sleep(0.1)
