"""
pages/process_page/process_input.py

Input handling for the process manager.
Processes keyboard input and navigation commands.
"""

import curses
from typing import List, Optional, Tuple

from frontend.pages.process_page.process_page_constants import PAGE_JUMP_SIZE
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
    Handle sort key inputs and return new sort mode.
    Maps C/M/P/N keys to their respective sort modes
    (cpu, mem, pid, name).
    """
    mode = None
    if key in (ord("c"), ord("C")):
        mode = "cpu"
    if key in (ord("m"), ord("M")):
        mode = "mem"
    if key in (ord("p"), ord("P")):
        mode = "pid"
    if key in (ord("n"), ord("N")):
        mode = "name"
    if key in (ord("i"), ord("I")):
        mode = "nice"
    return mode


def is_quit_or_nav_key(key: int) -> bool:
    """
    Check if key is a quit or navigation key.
    Returns True for keys that should exit the process viewer
    (Q for quit, D for dashboard, 1/3/4/5 for other pages).
    """
    return key in (
        ord("d"),
        ord("D"),
        ord("1"),
        ord("3"),
        ord("4"),
        ord("5"),
        ord("q"),
        ord("Q"),
    )


def handle_process_input(
    key: int, selected_index: int, processes: List[ProcessInfo]
) -> Tuple[int, Optional[str], bool, bool, bool, Optional[int]]:
    """
    Handle key input for navigation, sorting, killing, pausing, resuming, and quitting.

    Args:
        key: The key code pressed by the user
        selected_index: Currently selected process index
        processes: List of all processes

    Returns:
        Tuple containing:
        - new_selected: New selected index after navigation
        - new_sort_mode: New sort mode if sort key pressed, else None
        - kill_flag: True if kill key pressed
        - pause_flag: True if pause key pressed
        - resume_flag: True if resume key pressed
        - return_key: Key code if quit/nav key pressed, else None
    """
    new_selected = handle_navigation_keys(key, selected_index, len(processes))
    new_sort_mode = handle_sort_keys(key)
    kill_flag = key in (ord("k"), ord("K"))
    pause_flag = key in (ord("s"), ord("S"))
    resume_flag = key in (ord("r"), ord("R"))
    return_key = key if is_quit_or_nav_key(key) else None

    return new_selected, new_sort_mode, kill_flag, pause_flag, resume_flag, return_key
