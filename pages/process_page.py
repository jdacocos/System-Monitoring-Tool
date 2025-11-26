"""
process_page.py

Curses-based interactive process viewer.
Displays all running processes with sorting, scrolling, and optional killing.
Optimized for single-core systems using double buffering and cached process info.
"""

import curses
import time
from process import populate_process_list
from utils.ui_helpers import init_colors

# Threshold for CPU/mem change to trigger re-render
CPU_CHANGE_THRESHOLD = 0.1
MEM_CHANGE_THRESHOLD = 0.1

REFRESH_INTERVAL_ACTIVE = 1.0  # active processes
REFRESH_INTERVAL_IDLE = 5.0  # sleeping or idle processes


def draw_process_list(pad: curses.window, processes, selected_index, start, sort_mode):
    """Render the visible slice of processes to the pad."""
    height, width = pad.getmaxyx()
    pad.erase()

    # Header
    header = f"{'USER':<10} {'PID':<6} {'%CPU':>5} {'%MEM':>5} {'VSZ':>8} {'RSS':>8} {'TTY':<8} {'STAT':<6} {'START':<6} {'TIME':<8} COMMAND"
    pad.addstr(0, 0, header)
    pad.hline(1, 0, curses.ACS_HLINE, width)

    for idx, proc in enumerate(processes[start:], start=start):
        y = idx - start + 2
        if y >= height:
            break

        line = f"{proc.user:<10} {proc.pid:<6} {proc.cpu_percent:>5.1f} {proc.mem_percent:>5.1f} {proc.vsz:>8} {proc.rss:>8} {proc.tty:<8} {proc.stat:<6} {proc.start:<6} {proc.time:<8} {proc.command}"

        if idx == selected_index:
            pad.attron(curses.color_pair(6))
            pad.addstr(y, 0, line[:width])
            pad.attroff(curses.color_pair(6))
        else:
            pad.attron(curses.color_pair(5))
            pad.addstr(y, 0, line[:width])
            pad.attroff(curses.color_pair(5))

    # Footer help
    pad.attron(curses.color_pair(2))
    pad.addstr(
        height - 1, 0, "[↑/↓] Move   [C]PU  [M]em  [P]ID  [N]ame   [K]ill   [Q]uit"
    )
    pad.attroff(curses.color_pair(2))


def render_processes(stdscr: curses.window, nav_items, active_page):
    """Interactive process viewer with double buffering, caching, and selective rendering."""
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    selected_index = 0
    scroll_start = 0
    sort_mode = "cpu_percent"

    cached_processes = populate_process_list()
    last_rendered_state = {proc.pid: proc.stat for proc in cached_processes}
    last_refresh_time = time.time()

    # Create pad for double buffering
    pad_height = max(len(cached_processes) + 5, 100)
    pad_width = 200
    pad = curses.newpad(pad_height, pad_width)

    while True:
        now = time.time()
        # Determine refresh interval
        interval = (
            REFRESH_INTERVAL_ACTIVE
            if any(p.stat in ("R", "D") for p in cached_processes)
            else REFRESH_INTERVAL_IDLE
        )

        if now - last_refresh_time >= interval:
            cached_processes = populate_process_list()
            last_refresh_time = now

        # Sort processes
        reverse = sort_mode in ("cpu_percent", "mem_percent")
        cached_processes.sort(
            key=lambda p: (
                getattr(p, sort_mode) if hasattr(p, sort_mode) else getattr(p, "pid")
            ),
            reverse=reverse,
        )

        # Clamp selected index
        selected_index = max(0, min(selected_index, len(cached_processes) - 1))

        # Adjust scrolling
        height, _ = stdscr.getmaxyx()
        visible_lines = height - 5
        if selected_index < scroll_start:
            scroll_start = selected_index
        elif selected_index >= scroll_start + visible_lines:
            scroll_start = selected_index - visible_lines + 1

        # Draw processes to pad
        draw_process_list(
            pad, cached_processes, selected_index, scroll_start, sort_mode
        )

        # Refresh visible pad to screen (double buffering)
        pad.noutrefresh(0, 0, 0, 0, height - 1, pad_width - 1)
        stdscr.noutrefresh()
        curses.doupdate()

        # Handle input
        key = stdscr.getch()
        if key == -1:
            time.sleep(0.05)
            continue

        if key == curses.KEY_UP:
            selected_index -= 1
        elif key == curses.KEY_DOWN:
            selected_index += 1
        elif key in (ord("c"), ord("C")):
            sort_mode = "cpu_percent"
        elif key in (ord("m"), ord("M")):
            sort_mode = "mem_percent"
        elif key in (ord("p"), ord("P")):
            sort_mode = "pid"
        elif key in (ord("n"), ord("N")):
            sort_mode = "command"
        elif key in (ord("k"), ord("K")):
            try:
                import os

                os.kill(cached_processes[selected_index].pid, 9)
            except PermissionError:
                pass
        elif key in (ord("q"), ord("Q")):
            return  # quit
