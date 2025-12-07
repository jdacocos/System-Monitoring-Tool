"""
page_helpers.py

Utility functions for managing curses-based frontend pages.

Shows:
- Generic page loop for rendering and updating interactive pages
- Keyboard input handling
- Screen refreshes at configurable intervals

Integrates with the generic page loop to handle:
- Window creation and layout
- Page-specific content rendering
- Keyboard input handling
- Refresh cycles for curses windows

Dependencies:
- curses (standard library)
- time (standard library)
- frontend.utils.input_helpers
- frontend.utils.ui_helpers
"""

import curses
import time
from frontend.utils.input_helpers import handle_input, GLOBAL_KEYS
from frontend.utils.ui_helpers import init_colors, draw_content_window

# pylint: disable=too-many-arguments, too-many-positional-arguments


def run_page_loop(
    stdscr: curses.window,
    title: str,
    nav_items: list[tuple[str, str, str]],
    active_page: str,
    render_content_fn,
    sleep_time: float = 0.3,
) -> int:
    """
    Generic curses page loop for rendering interactive pages.

    Handles:
    - Initializing colors
    - Creating and updating the content window
    - Calling page-specific rendering functions
    - Capturing keyboard input
    - Refreshing the screen at configurable intervals

    Args:
        stdscr (curses.window): Main curses window provided by curses.wrapper.
        title (str): Title of the page/window.
        nav_items (list[tuple[str, str, str]]): List of navigation items (id, name, key).
        active_page (str): Identifier for the currently active page.
        render_content_fn (Callable): Function to render page-specific content;
            called with content_win.
        sleep_time (float, optional): Delay between screen refreshes in seconds. Defaults to 0.3.

    Returns:
        int: The key code pressed that triggered an exit, or continues looping indefinitely.
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
