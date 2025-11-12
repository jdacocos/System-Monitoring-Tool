import curses
import psutil
import time

from utils.ui_helpers import (init_colors, draw_content_window, draw_section_header)
from utils.input_helpers import handle_input, GLOBAL_KEYS

cpu_history = {}

def get_all_processes(sort_mode: str = "cpu") -> list[dict]:
    """Fetch and return a sorted list of running processes based on the sort mode."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            info['cpu_percent'] = info.get('cpu_percent', 0.0) or 0.0
            info['memory_percent'] = info.get('memory_percent', 0.0) or 0.0
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    key_map = {
        "cpu": lambda p: p['cpu_percent'],
        "mem": lambda p: p['memory_percent'],
        "pid": lambda p: p['pid'],
        "name": lambda p: p['name'].lower(),
    }
    reverse = sort_mode in ("cpu", "mem")
    return sorted(processes, key=key_map[sort_mode], reverse=reverse)


def draw_process_list(win: curses.window, processes: list[dict],
                      selected_index: int, start: int, sort_mode: str) -> None:
    """Render a scrollable list of processes with highlighting."""
    height, width = win.getmaxyx()

    draw_section_header(win, 1, f"Running Processes (Sort by {sort_mode.upper()})")
    win.addstr(2, 2, f"{'PID':<8}{'NAME':<30}{'CPU%':>8}{'MEM%':>10}")
    win.hline(3, 2, curses.ACS_HLINE, width - 4)

    visible_lines = height - 6
    end = min(start + visible_lines, len(processes))

    for i, proc in enumerate(processes[start:end], start=start):
        y = 4 + (i - start)
        is_selected = (i == selected_index)
        if is_selected:
            win.attron(curses.color_pair(6))  # highlight color
        else:
            win.attron(curses.color_pair(5))  # normal text

        win.addstr(y, 2, f"{proc['pid']:<8}{proc['name'][:28]:<30}"
                         f"{proc['cpu_percent']:>8.2f}{proc['memory_percent']:>10.2f}")

        if is_selected:
            win.attroff(curses.color_pair(6))
        else:
            win.attroff(curses.color_pair(5))

    help_y = height - 2
    win.attron(curses.color_pair(2))
    win.addstr(help_y, 2, "[↑/↓] Move   [C]PU  [M]em  [P]ID  [N]ame  [K]ill")
    win.attroff(curses.color_pair(2))


def render_processes(stdscr: curses.window,
                     nav_items: list[tuple[str, str, str]],
                     active_page: str) -> int:
    """Interactive process viewer with sorting, scrolling, highlight, and kill support."""

    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)  # <<<<<< allow screen to refresh even without key press

    selected_index = 0
    scroll_start = 0
    sort_mode = "cpu"
    refresh_interval = 1.0
    last_refresh = 0.0
    cached_processes: list[dict] = []
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
        if needs_refresh or (now - last_refresh) >= refresh_interval or not cached_processes:
            cached_processes = get_all_processes(sort_mode)
            last_refresh = now
            needs_refresh = False

        processes = cached_processes
        if not processes:
            content_win.addstr(2, 2, "No processes found.")
            content_win.refresh()
            time.sleep(0.5)
            continue

        # Clamp selected index
        selected_index = max(0, min(selected_index, len(processes) - 1))

        visible_lines = content_win.getmaxyx()[0] - 6
        if selected_index < scroll_start:
            scroll_start = selected_index
        elif selected_index >= scroll_start + visible_lines:
            scroll_start = selected_index - visible_lines + 1

        draw_process_list(content_win, processes, selected_index, scroll_start, sort_mode)

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        key = stdscr.getch()
        if key == -1:
            # no key pressed, keep refreshing
            time.sleep(0.1)
            continue

        # Navigation
        if key == curses.KEY_UP:
            selected_index -= 1
        elif key == curses.KEY_DOWN:
            selected_index += 1

        # Sorting
        elif key in (ord('c'), ord('C')):
            sort_mode = "cpu"
            needs_refresh = True
        elif key in (ord('m'), ord('M')):
            sort_mode = "mem"
            needs_refresh = True
        elif key in (ord('p'), ord('P')):
            sort_mode = "pid"
            needs_refresh = True
        elif key in (ord('n'), ord('N')):
            sort_mode = "name"
            needs_refresh = True

        # Kill selected process
        elif key in (ord('k'), ord('K')):
            try:
                pid = processes[selected_index]['pid']
                psutil.Process(pid).kill()
                needs_refresh = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Switch pages or quit
        elif key in (ord('d'), ord('D'), ord('1'), ord('3'), ord('4'), ord('5'), ord('q'), ord('Q')):
            return key

        time.sleep(0.1)