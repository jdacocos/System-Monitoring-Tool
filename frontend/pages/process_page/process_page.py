"""
pages/process_page.py

Main loop for interactive process manager UI.

Entry point that coordinates display, input, and state management
for the curses-based process viewer.
"""

import curses
import os
import time
from typing import Optional, Tuple
from dataclasses import dataclass

from frontend.utils.ui_helpers import draw_content_window
from frontend.utils.input_helpers import handle_input, GLOBAL_KEYS
from frontend.pages.process_page.process_page_constants import (
    DRAW_INTERVAL,
    VISIBLE_LINE_OFFSET,
)
from frontend.pages.process_page.process_display import (
    DrawParams,
    perform_draw,
    display_empty_process_list,
)
from frontend.pages.process_page.process_state import (
    init_process_viewer,
    clamp_and_scroll,
    refresh_process_state,
    build_display_state,
    process_user_input,
)


def handle_window_resize(stdscr: curses.window) -> Tuple[Optional[int], Optional[int]]:
    """
    Handle terminal size and return dimensions, or None if too small.
    Checks terminal dimensions and displays warning if window
    is too small to display the process manager.
    """
    try:
        height, width = stdscr.getmaxyx()
    except curses.error:
        return None, None

    if height < 10 or width < 80:
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, "Terminal too small. Please resize.")
            stdscr.refresh()
        except curses.error:
            pass
        return None, None

    return height, width


@dataclass
class WindowConfig:
    """Configuration for window management."""

    nav_items: list
    active_page: str
    win: Optional[curses.window] = None
    last_dimensions: Optional[Tuple[int, int]] = None


def create_or_get_window(
    stdscr: curses.window,
    config: WindowConfig,
    current_dimensions: Tuple[int, int],
) -> Tuple[Optional[curses.window], Optional[Tuple[int, int]]]:
    """
    Create or reuse content window based on dimension changes.
    Creates a new content window only when dimensions change,
    otherwise reuses existing window for efficiency.
    """
    if config.win is None or config.last_dimensions != current_dimensions:
        win = draw_content_window(
            stdscr, "Process Manager", config.nav_items, config.active_page
        )
        if win is None:
            return None, config.last_dimensions
        return win, current_dimensions
    return config.win, config.last_dimensions


def initialize_render_state(stdscr: curses.window) -> dict:
    """
    Initialize the rendering state for the main loop.
    Sets up initial state including viewer state and timing variables.
    """
    state = init_process_viewer(stdscr)
    current_pid = os.getpid()

    return {
        "viewer_state": state,
        "current_pid": current_pid,
        "last_draw_time": 0.0,
    }


def handle_empty_window(stdscr: curses.window) -> Optional[int]:
    """
    Handle case when content window creation fails.
    Checks for global key input and returns appropriate key code,
    or None if should continue loop.
    """
    key = handle_input(stdscr, GLOBAL_KEYS)
    if key != -1:
        return key
    time.sleep(0.05)
    return None


def should_redraw(now: float, last_draw_time: float, needs_refresh: bool) -> bool:
    """
    Determine if screen should be redrawn.
    Checks if enough time has passed or if a forced refresh is needed.
    """
    return (now - last_draw_time) >= DRAW_INTERVAL or needs_refresh


def handle_resize_key(window_config: WindowConfig):
    """
    Handle terminal resize event.
    Resets window state to force recreation on next iteration.
    """
    window_config.win = None
    window_config.last_dimensions = None


def process_input_key(
    key: int, viewer_state: dict, current_pid: int, window_config: WindowConfig
) -> Optional[int]:
    """
    Process user input and update state accordingly.
    Handles resize events and user input, returns quit key if applicable.
    """
    if key == curses.KEY_RESIZE:
        handle_resize_key(window_config)
        viewer_state["needs_refresh"] = True
        return None

    quit_key = process_user_input(key, viewer_state, current_pid)

    if quit_key is not None:
        return quit_key

    viewer_state["needs_refresh"] = True
    return None


def _get_window(
    stdscr: curses.window, window_config: WindowConfig
) -> Optional[tuple[curses.window, tuple[int, int]]]:
    """
    Handle terminal size and return a usable content window.

    Returns a tuple of the window and its dimensions, or (None, None)
    if the terminal is too small or the window cannot be created.
    """
    dimensions = handle_window_resize(stdscr)
    if dimensions == (None, None):
        time.sleep(0.5)
        return None, None

    win, last_dimensions = create_or_get_window(stdscr, window_config, dimensions)
    if win is None:
        return None, last_dimensions
    return win, dimensions


def _refresh_process_data(viewer_state: dict) -> list:
    """
    Refresh cached process data and return the list of processes.
    """
    refresh_process_state(viewer_state)
    return viewer_state["cached_processes"]


def _handle_empty_process_list(win: curses.window, processes: list) -> bool:
    """
    Display empty process message if no processes exist.

    Returns True if processes were empty and handled, else False.
    """
    if not processes:
        win_height, _ = win.getmaxyx()
        display_empty_process_list(win, win_height)
        time.sleep(0.1)
        return True
    return False


def _draw_processes_if_needed(
    win: curses.window, render_state: dict, viewer_state: dict, processes: list
):
    """
    Check if redraw is needed and render the process list.
    """
    now = time.time()
    if should_redraw(
        now, render_state["last_draw_time"], viewer_state["needs_refresh"]
    ):
        display_state = build_display_state(viewer_state, processes, now)
        draw_params = DrawParams(
            processes=processes,
            selected_index=viewer_state["selected_index"],
            scroll_start=viewer_state["scroll_start"],
            sort_mode=viewer_state["sort_mode"],
        )
        perform_draw(win, draw_params, display_state)
        render_state["last_draw_time"] = now
        viewer_state["needs_refresh"] = False


def _handle_input(
    stdscr: curses.window,
    viewer_state: dict,
    current_pid: int,
    window_config: WindowConfig,
) -> Optional[int]:
    """
    Poll for user input and process it.
    """
    key = stdscr.getch()
    if key != -1:
        return process_input_key(key, viewer_state, current_pid, window_config)
    return None


def handle_main_loop_iteration(
    stdscr: curses.window,
    window_config: WindowConfig,
    render_state: dict,
) -> Optional[int]:
    """
    Execute one iteration of the main render loop for the process manager.

    Handles window management, process display, scrolling, and user input.
    """
    viewer_state = render_state["viewer_state"]

    # Get window
    win, dims = _get_window(stdscr, window_config)
    if win is None:
        return handle_empty_window(stdscr)
    window_config.win = win
    window_config.last_dimensions = dims

    # Get visible lines
    try:
        win_height, _ = win.getmaxyx()
    except curses.error:
        window_config.win = None
        return None
    visible_lines = win_height - VISIBLE_LINE_OFFSET

    processes = _refresh_process_data(viewer_state)

    if _handle_empty_process_list(win, processes):
        return None

    clamp_and_scroll(viewer_state, visible_lines)

    _draw_processes_if_needed(win, render_state, viewer_state, processes)

    return _handle_input(
        stdscr, viewer_state, render_state["current_pid"], window_config
    )


def render_processes(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """
    Interactive curses process viewer with sorting, scrolling, and process control.

    Main entry point for the process manager page. Initializes the viewer,
    runs the main loop, and handles user interaction.

    Args:
        stdscr: Main curses window
        nav_items: Navigation menu items
        active_page: Currently active page identifier

    Returns:
        Key code for page navigation or quit
    """
    render_state = initialize_render_state(stdscr)
    window_config = WindowConfig(nav_items=nav_items, active_page=active_page)

    while True:
        quit_key = handle_main_loop_iteration(stdscr, window_config, render_state)

        if quit_key is not None:
            return quit_key
