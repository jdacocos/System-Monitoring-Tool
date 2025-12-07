"""
main.py

Entry point for the terminal system monitor application.

Shows:
- Initializing the curses environment
- Running the main interface loop from frontend.interface
- Handling screen setup and teardown automatically via curses.wrapper

Dependencies:
- Standard Python libraries: curses
- frontend.interface for the main interface loop
"""

import curses
from frontend.interface import run_interface


def main(stdscr: curses.window) -> None:
    """
    Main entry point for the curses interface.

    Args:
        stdscr (curses._CursesWindow): The main curses screen window provided by curses.wrapper.

    Returns:
        None
    """

    # Run the interface logic
    run_interface(stdscr)


# Initialize curses and run the main function
if __name__ == "__main__":
    curses.wrapper(main)
