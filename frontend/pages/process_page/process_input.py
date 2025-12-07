"""
pages/process_page/process_input.py

Input handling for the process manager.
Processes keyboard input and navigation commands.
"""

import curses
from typing import List, Optional, Tuple

from frontend.utils.input_helpers import GLOBAL_KEYS
from frontend.pages.process_page.process_page_constants import (
    PAGE_JUMP_SIZE,
    ACTION_KEYS,
    SORT_KEY_MAPPING,
)
from backend.process_struct import ProcessInfo


def handle_navigation_keys(key: int, selected_index: int, num_processes: int) -> int:
    """
    Handle navigation key inputs and return new selected index.
    Processes arrow keys, page up/down, home/end keys and
    calculates the new selection index with bounds checking.
    """
    new_index = selected_index

    if key == curses.KEY_UP:
        new_index = max(0, selected_index - 1)
    elif key == curses.KEY_DOWN:
        new_index = min(selected_index + 1, num_processes - 1)
    elif key == curses.KEY_PPAGE:  # Page Up
        new_index = max(0, selected_index - PAGE_JUMP_SIZE)
    elif key == curses.KEY_NPAGE:  # Page Down
        new_index = min(selected_index + PAGE_JUMP_SIZE, num_processes - 1)
    elif key == curses.KEY_HOME:
        new_index = 0
    elif key == curses.KEY_END:
        new_index = num_processes - 1

    return new_index


def handle_sort_keys(key: int) -> Optional[str]:
    """
    Return the sort mode corresponding to a key press.
    """
    return SORT_KEY_MAPPING.get(key)


def is_quit_or_nav_key(key: int) -> bool:
    """
    Check if key is a quit or navigation key.
    Returns True for keys that should exit the process viewer
    or navigate to other pages.
    """
    return key in GLOBAL_KEYS


def handle_process_input(
    key: int, selected_index: int, processes: List[ProcessInfo]
) -> Tuple[int, Optional[str], bool, bool, bool, bool, Optional[int]]:
    """
    Handle all key input for navigation, sorting, actions, and quitting.
    Returns: (new_index, sort_mode, kill_flag, pause_flag, resume_flag, renice_flag, return_key)
    """
    new_selected = handle_navigation_keys(key, selected_index, len(processes))
    new_sort_mode = handle_sort_keys(key)

    # Use constants for action keys
    kill_flag = key in ACTION_KEYS["kill"]
    pause_flag = key in ACTION_KEYS["pause"]
    resume_flag = key in ACTION_KEYS["resume"]
    renice_flag = key in ACTION_KEYS.get("renice", [ord("r"), ord("R")])

    return_key = key if is_quit_or_nav_key(key) else None

    return (
        new_selected,
        new_sort_mode,
        kill_flag,
        pause_flag,
        resume_flag,
        renice_flag,
        return_key,
    )
