# pages/ui_helpers.py
import curses

FOOTER_TEXT = "[d] Dashboard  [1] CPU  [2] Processes  [3] Network  [4] Memory  [q] Quit"

def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)

def draw_title(stdscr: curses.window, text: str) -> None:
    height, width = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, width // 2 - len(text)//2, text)
    stdscr.attroff(curses.color_pair(1))

def draw_box(stdscr):
    stdscr.attron(curses.color_pair(2))
    stdscr.box()
    stdscr.attroff(curses.color_pair(2))

def draw_bar(stdscr: curses.window, y: int, x: int, 
             label: str, value: float, width: int = 30) -> None:
    filled = int((value / 100) * width)
    bar = "█" * filled + "-" * (width - filled)
    color = 3 if value < 80 else 4
    stdscr.attron(curses.color_pair(color))
    stdscr.addstr(y, x, f"{label:<10}: [{bar}] {value:5.1f}%")
    stdscr.attroff(curses.color_pair(color))

def draw_footer(stdscr: curses.window) -> None:
    height, _ = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(height - 2, 4, FOOTER_TEXT)
    stdscr.attroff(curses.color_pair(1))

def draw_section_header(stdscr: curses.window, y: int, text: str) -> None:
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(y, 4, text)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

def format_bytes(num_bytes: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024:
            return f"{num_bytes:6.1f} {unit}"
        num_bytes /= 1024
