import curses

def handle_input(stdscr: curses.window, valid_keys: tuple[int, ...] = ()) -> int:
    """
    Wait for and process user key input.
    Returns the pressed key if it is in valid_keys (if provided),
    otherwise returns -1 to continue the loop.
    """
    key = stdscr.getch()
    if valid_keys:
        return key if key in valid_keys else -1
    return key


# Optional global constant for shared navigation keys
GLOBAL_KEYS = (ord('d'), ord('1'), ord('2'), ord('3'), ord('4'), ord('q'))
