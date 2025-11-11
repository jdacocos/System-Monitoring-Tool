import curses
import psutil
import time
from utils.ui_helpers import init_colors, draw_title, draw_box, draw_bar, draw_footer
from utils.input_helpers import handle_input, GLOBAL_KEYS

# Replace this function with later with our own calculations
def get_memory_stats() -> dict:
    """Fetch memory and swap usage statistics."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {"mem": mem, "swap": swap}


def render_memory_details(stdscr: curses.window, mem) -> None:
    """Render main RAM usage bar and memory details."""
    draw_bar(stdscr, 3, 4, "RAM", mem.percent)
    total_gb = mem.total / (1024 ** 3)
    used_gb = mem.used / (1024 ** 3)
    free_gb = mem.available / (1024 ** 3)
    stdscr.addstr(5, 6, f"Total: {total_gb:6.2f} GB")
    stdscr.addstr(6, 6, f"Used : {used_gb:6.2f} GB")
    stdscr.addstr(7, 6, f"Free : {free_gb:6.2f} GB")


def render_swap_details(stdscr: curses.window, swap) -> None:
    """Render swap memory usage bar and details."""
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(9, 4, "Swap Usage")
    stdscr.attroff(curses.color_pair(3))

    draw_bar(stdscr, 10, 4, "Swap", swap.percent)
    stdscr.addstr(12, 6, f"Total Swap: {swap.total / (1024 ** 3):6.2f} GB")
    stdscr.addstr(13, 6, f"Used Swap : {swap.used / (1024 ** 3):6.2f} GB")
    stdscr.addstr(14, 6, f"Free Swap : {swap.free / (1024 ** 3):6.2f} GB")


def render_memory(stdscr: curses.window) -> int:
    """
    Render the Memory Monitor page.
    Displays RAM and swap memory usage with details.
    Returns the pressed key for navigation.
    """
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        stdscr.erase()
        stdscr.bkgd(' ', curses.color_pair(1))
        draw_title(stdscr, "MEMORY MONITOR")
        draw_box(stdscr)

        stats = get_memory_stats()
        render_memory_details(stdscr, stats["mem"])
        render_swap_details(stdscr, stats["swap"])

        draw_footer(stdscr)
        stdscr.refresh()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.3)
