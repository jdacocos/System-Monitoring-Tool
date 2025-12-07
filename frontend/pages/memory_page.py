"""
memory_page.py

Memory monitoring page for the interactive terminal UI.

Shows RAM and swap usage in real-time, including:
- Physical memory usage bars and details (total, used, free)
- Swap memory usage bars and details (total, used, free)

Integrates with the generic page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes
"""

import curses

from frontend.utils.ui_helpers import (
    draw_bar,
    draw_section_header,
    format_bytes,
)
from frontend.utils.page_helpers import run_page_loop
from backend.memory_info import (
    get_virtual_memory,
    get_swap_memory,
)


def get_memory_stats() -> dict:
    """Fetch memory and swap usage statistics."""

    mem = get_virtual_memory()
    swap = get_swap_memory()
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


def render_memory_page(content_win: curses.window) -> None:
    """
    Render the Memory Monitor page content inside the given content window.
    """
    mem = get_virtual_memory()
    swap = get_swap_memory()

    # Physical memory
    draw_section_header(content_win, 1, "Physical Memory")
    draw_bar(content_win, 2, 2, "RAM", mem.percent)
    content_win.addstr(3, 4, f"Total : {format_bytes(mem.total)}")
    content_win.addstr(4, 4, f"Used  : {format_bytes(mem.used)}")
    content_win.addstr(5, 4, f"Free  : {format_bytes(mem.available)}")

    # Swap memory
    draw_section_header(content_win, 8, "Swap Memory")
    draw_bar(content_win, 9, 2, "Swap", swap.percent)
    content_win.addstr(10, 4, f"Total : {format_bytes(swap.total)}")
    content_win.addstr(11, 4, f"Used  : {format_bytes(swap.used)}")
    content_win.addstr(12, 4, f"Free  : {format_bytes(swap.free)}")


def render_memory(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """
    Launch the Memory Monitor page loop using the generic `run_page_loop`.
    """
    return run_page_loop(
        stdscr,
        title="Memory Monitor",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_memory_page,
        sleep_time=0.3,
    )
