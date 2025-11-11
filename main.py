import curses
from interface import run_interface

def main(stdscr: curses.window) -> None:
    # Run the interface logic
    run_interface(stdscr)

# Initialize curses and run the main function
if __name__ == "__main__":
    curses.wrapper(main)