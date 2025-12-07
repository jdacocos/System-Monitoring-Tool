import curses
import time
from frontend.utils.input_helpers import handle_input, GLOBAL_KEYS
from frontend.utils.ui_helpers import init_colors, draw_content_window


def run_page_loop(
    stdscr: curses.window,
    title: str,
    nav_items: list[tuple[str, str, str]],
    active_page: str,
    render_content_fn,
    sleep_time: float = 0.3,
) -> int:
    """Generic curses page loop for CPU, memory, disk, network, or dashboard pages.

    Parameters:
        stdscr: main curses window
        title: window title
        nav_items: navigation menu items
        active_page: string identifier of active page
        render_content_fn: function called with content_win to draw page-specific content
        sleep_time: delay between refreshes

    Returns:
        key pressed if exit requested, else loop indefinitely
    """
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        content_win = draw_content_window(stdscr, title, nav_items, active_page)
        if content_win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.2)
            continue

        render_content_fn(content_win)

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(sleep_time)
