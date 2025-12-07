"""
input_helpers.py

Utility functions for handling keyboard input within the curses-based frontend.

Shows:
- Capturing and validating user key input
- Defining shared navigation keys for the interface

Integrates with the generic page loop to handle:
- Keyboard input processing
- Loop continuation control

Dependencies:
- curses (standard library)
"""

import curses


def handle_input(stdscr: curses.window, valid_keys: tuple[int, ...] = ()) -> int:
    """
    Wait for and process user key input in a curses window.

    Captures a single key press from the user. If a tuple of valid keys
    is provided, only returns the key if it is in the list; otherwise,
    returns -1 to indicate invalid or unhandled input.

    Args:
        stdscr (curses.window): The main curses window from which input is read.
        valid_keys (tuple[int, ...], optional): Tuple of integer key codes that are valid.
            Defaults to an empty tuple, meaning all keys are accepted.

    Returns:
        int: The key code of the pressed key if valid, or -1 if invalid/unhandled.
    """

    key = stdscr.getch()
    if valid_keys:
        return key if key in valid_keys else -1
    return key


# Optional global constant for shared navigation keys
GLOBAL_KEYS = (
    ord("d"),
    ord("D"),
    ord("1"),
    ord("2"),
    ord("3"),
    ord("4"),
    ord("5"),
    ord("q"),
    ord("Q"),
)
