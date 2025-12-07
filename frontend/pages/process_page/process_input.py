"""
process_input.py

Handles keyboard input for the process manager page.
Processes navigation, sorting, and action commands.

Shows:
- Navigation via arrow keys, page up/down, home/end
- Sorting of process list
- Process actions: kill, pause, resume, renice
- Quit or return key handling

Integrates with the generic page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes

Dependencies:
- curses
- typing
- frontend.utils.input_helpers (GLOBAL_KEYS)
- frontend.pages.process_page.process_page_constants
- backend.process_struct (ProcessInfo)
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
    Update the selected process index based on navigation key input.

    Args:
        key (int): The pressed key code.
        selected_index (int): Current selected process index.
        num_processes (int): Total number of processes in the list.

    Returns:
        int: Updated selected index after applying navigation logic.
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
    Map a key press to a sort mode, if applicable.

    Args:
        key (int): The key code pressed.

    Returns:
        Optional[str]: Sort mode string if the key corresponds to sorting, else None.
    """

    return SORT_KEY_MAPPING.get(key)


def is_quit_or_nav_key(key: int) -> bool:
    """
    Determine if the key is a quit or navigation key.

    Args:
        key (int): The key code pressed.

    Returns:
        bool: True if key is in GLOBAL_KEYS, else False.
    """

    return key in GLOBAL_KEYS


def handle_process_input(
    key: int, selected_index: int, processes: List[ProcessInfo]
) -> Tuple[int, Optional[str], bool, bool, bool, bool, Optional[int]]:
    """
    Handle key input for navigation, sorting, actions, and quitting.

    Args:
        key (int): Key code pressed.
        selected_index (int): Currently selected process index.
        processes (List[ProcessInfo]): List of process information.

    Returns:
        Tuple[int, Optional[str], bool, bool, bool, bool, Optional[int]]:
        - new_selected (int): Updated selected process index.
        - new_sort_mode (Optional[str]): Sort mode if sorting key pressed.
        - kill_flag (bool): True if kill action key pressed.
        - pause_flag (bool): True if pause action key pressed.
        - resume_flag (bool): True if resume action key pressed.
        - renice_flag (bool): True if renice action key pressed.
        - return_key (Optional[int]): Key code if quit/navigation key pressed, else None.
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
