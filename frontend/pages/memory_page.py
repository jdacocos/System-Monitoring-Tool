import curses
import psutil
import time

from utils.ui_helpers import (
    init_colors,
    draw_content_window,
    draw_bar,
    draw_section_header,
    format_bytes,
)
from utils.input_helpers import handle_input, GLOBAL_KEYS


def get_memory_stats() -> dict:
    """Fetch memory and swap usage statistics."""

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {"mem": mem, "swap": swap}


def render_memory_details(win: curses.window, mem) -> None:
    """Render main RAM usage bar and memory details."""

    draw_section_header(win, 1, "Physical Memory")
    draw_bar(win, 2, 2, "RAM", mem.percent)
    win.addstr(3, 4, f"Total : {format_bytes(mem.total)}")
    win.addstr(4, 4, f"Used  : {format_bytes(mem.used)}")
    win.addstr(5, 4, f"Free  : {format_bytes(mem.available)}")


def render_swap_details(win: curses.window, swap) -> None:
    """Render swap memory usage bar and details."""

    draw_section_header(win, 8, "Swap Memory")
    draw_bar(win, 9, 2, "Swap", swap.percent)
    win.addstr(10, 4, f"Total : {format_bytes(swap.total)}")
    win.addstr(11, 4, f"Used  : {format_bytes(swap.used)}")
    win.addstr(12, 4, f"Free  : {format_bytes(swap.free)}")


def render_memory(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """Render the Memory Monitor page."""

    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        content_win = draw_content_window(
            stdscr,
            title="Memory Monitor",
            nav_items=nav_items,
            active_page=active_page,
        )

        if content_win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.2)
            continue

        stats = get_memory_stats()
        render_memory_details(content_win, stats["mem"])
        render_swap_details(content_win, stats["swap"])

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.3)
