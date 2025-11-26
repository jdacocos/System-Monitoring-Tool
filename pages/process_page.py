"""
process_pages.py

Curses-based process viewer displaying full ProcessInfo columns:
USER, PID, %CPU, %MEM, VSZ, RSS, TTY, STAT, START, TIME, COMMAND.
"""

import curses
import time
from typing import List

from utils.ui_helpers import init_colors, draw_content_window, draw_section_header
from utils.input_helpers import handle_input, GLOBAL_KEYS

from process import populate_process_list
from process_struct import ProcessInfo

# Sorting keys mapped to ProcessInfo attributes
SORT_KEYS = {
    "cpu": "cpu_percent",
    "mem": "mem_percent",
    "pid": "pid",
    "name": "command",
}


def draw_process_list(win: curses.window,
                      processes: List[ProcessInfo],
                      selected_index: int,
                      start: int,
                      sort_mode: str) -> None:
    """Render a scrollable list of processes with highlighting."""
    height, width = win.getmaxyx()

    draw_section_header(win, 1, f"Running Processes (Sort by {sort_mode.upper()})")
    header = f"{'USER':<10} {'PID':<6} {'%CPU':>5} {'%MEM':>5} {'VSZ':>8} {'RSS':>8} {'TTY':<8} {'STAT':<6} {'START':<6} {'TIME':<8} COMMAND"
    win.addstr(2, 2, header)
    win.hline(3, 2, curses.ACS_HLINE, width - 4)

    visible_lines = height - 6
    end = min(start + visible_lines, len(processes))

    for i, proc in enumerate(processes[start:end], start=start):
        y = 4 + (i - start)
        is_selected = (i == selected_index)
        color = 6 if is_selected else 5
        win.attron(curses.color_pair(color))

        tty_display = proc.tty[:7] if proc.tty else "?"
        command_display = proc.command[:width - 80] if proc.command else ""

        line = (
            f"{proc.user:<10} "
            f"{proc.pid:<6} "
            f"{proc.cpu_percent:>5.1f} "
            f"{proc.mem_percent:>5.1f} "
            f"{proc.vsz:>8} "
            f"{proc.rss:>8} "
            f"{tty_display:<8} "
            f"{proc.stat:<6} "
            f"{proc.start:<6} "
            f"{proc.time:<8} "
            f"{command_display}"
        )

        win.addstr(y, 2, line)
        win.attroff(curses.color_pair(color))

    help_y = height - 2
    win.attron(curses.color_pair(2))
    win.addstr(help_y, 2, "[↑/↓] Move   [C]PU  [M]em  [P]ID  [N]ame   [Q] Quit")
    win.attroff(curses.color_pair(2))


def render_processes(stdscr: curses.window,
                     nav_items: list[tuple[str, str, str]],
                     active_page: str) -> int:
    """Interactive process viewer with sorting, scrolling, highlight, and safe refresh."""
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    selected_index = 0
    scroll_start = 0
    sort_mode = "cpu"
    refresh_interval = 1.0
    last_refresh = 0.0
    cached_processes: List[ProcessInfo] = []
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
            cached_processes = populate_process_list()
            last_refresh = now
            needs_refresh = False

        processes = cached_processes

        if not processes:
            content_win.addstr(2, 2, "No processes found.")
            content_win.refresh()
            time.sleep(0.5)
            continue

        # Sort processes
        key_attr = SORT_KEYS.get(sort_mode, "cpu_percent")
        reverse = sort_mode in ("cpu", "mem")
        if key_attr == "command":  # case-insensitive
            processes.sort(key=lambda p: p.command.lower(), reverse=reverse)
        else:
            processes.sort(key=lambda p: getattr(p, key_attr), reverse=reverse)

        # Clamp selected index
        selected_index = max(0, min(selected_index, len(processes) - 1))

        # Handle scrolling
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
            time.sleep(0.05)
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

        # Quit
        elif key in (ord('q'), ord('Q')):
            return key

        # Clamp selected_index inside valid range
        selected_index = max(0, min(selected_index, len(processes) - 1))
