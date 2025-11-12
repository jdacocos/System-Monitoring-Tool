"""Utility helpers for rendering curses based user interfaces."""

from __future__ import annotations

import curses
from datetime import datetime
from typing import Iterable, Sequence

SIDEBAR_WIDTH = 22
MIN_HEIGHT = 22
MIN_WIDTH = 80


def init_colors() -> None:
    """Initialize the color palette used throughout the application."""

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Header / footer
    curses.init_pair(2, curses.COLOR_CYAN, -1)                   # Accent text
    curses.init_pair(3, curses.COLOR_GREEN, -1)                  # Healthy metrics
    curses.init_pair(4, curses.COLOR_RED, -1)                    # Critical metrics
    curses.init_pair(5, curses.COLOR_WHITE, -1)                  # Default text
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Active navigation
    curses.init_pair(7, curses.COLOR_BLUE, -1)                   # Sidebar text


def draw_header(stdscr: curses.window, title: str) -> None:
    """Render the top header banner with a timestamp."""

    height, width = stdscr.getmaxyx()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.hline(0, 0, " ", width)
    stdscr.addstr(0, 2, title[: max(0, width - 4)])
    stdscr.addstr(0, max(2, width - len(timestamp) - 2), timestamp)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)


def draw_sidebar(stdscr: curses.window,
                 nav_items: Sequence[tuple[str, str, str]],
                 active_page: str) -> None:
    """Render the navigation sidebar highlighting the active page."""

    height, _ = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(7))
    for y in range(1, height - 1):
        stdscr.addstr(y, 0, " " * SIDEBAR_WIDTH)
    stdscr.attroff(curses.color_pair(7))

    stdscr.attron(curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(1, 2, "Navigation")
    stdscr.attroff(curses.A_BOLD | curses.color_pair(2))

    for idx, (page_id, label, key) in enumerate(nav_items):
        y = 3 + idx * 2
        if y >= height - 2:
            break

        display = f"[{key.upper():>2}] {label:<12}"[: SIDEBAR_WIDTH - 2]
        attr = curses.color_pair(6) if page_id == active_page else curses.color_pair(5)
        stdscr.attron(attr)
        stdscr.addstr(y, 1, display.ljust(SIDEBAR_WIDTH - 2))
        stdscr.attroff(attr)

    for y in range(1, height - 1):
        stdscr.addch(y, SIDEBAR_WIDTH - 1, curses.ACS_VLINE)


def draw_footer(stdscr: curses.window,
                nav_items: Iterable[tuple[str, str, str]]) -> None:
    """Render a footer with contextual key bindings."""

    height, width = stdscr.getmaxyx()
    instructions = "  ".join(
        f"[{key}] {label}" for _, label, key in nav_items
    ) + "  [q] Quit"

    stdscr.attron(curses.color_pair(1))
    stdscr.hline(height - 1, 0, " ", width)
    stdscr.addstr(height - 1, 2, instructions[: max(0, width - 4)])
    stdscr.attroff(curses.color_pair(1))


def draw_content_window(stdscr: curses.window, title: str,
                        nav_items: Sequence[tuple[str, str, str]],
                        active_page: str) -> curses.window | None:
    """
    Draw the base layout consisting of header, sidebar, content area, and footer.

    Returns the content window where individual pages can render information.
    If the terminal is too small, a message is rendered and ``None`` is returned.
    """

    height, width = stdscr.getmaxyx()
    if height < MIN_HEIGHT or width < MIN_WIDTH:
        stdscr.erase()
        msg = (
            f"Increase terminal size to at least {MIN_WIDTH}x{MIN_HEIGHT} "
            f"(current: {width}x{height})."
        )
        stdscr.addstr(
            height // 2,
            max(0, (width - len(msg)) // 2),
            msg[: max(0, width - 2)]
        )
        stdscr.refresh()
        return None

    # Clear background each frame
    stdscr.erase()
    stdscr.bkgd(" ", curses.color_pair(5))

    # Draw dynamic elements (header, sidebar, footer)
    draw_sidebar(stdscr, nav_items, active_page)
    draw_footer(stdscr, nav_items)
    
    # Instead of caching the header once, we redraw it each frame with updated timestamp
    height, width = stdscr.getmaxyx()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.hline(0, 0, " ", width)
    stdscr.addstr(0, 2, title[: max(0, width - 4)])
    stdscr.addstr(0, max(2, width - len(timestamp) - 2), timestamp)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

    # Create bordered content area
    content_height = height - 4
    content_width = width - SIDEBAR_WIDTH - 3
    content_win = stdscr.derwin(content_height, content_width, 2, SIDEBAR_WIDTH + 1)
    content_win.erase()
    content_win.box()

    label = f" {title} "
    content_win.attron(curses.color_pair(2))
    content_win.addstr(0, 2, label[: max(0, content_width - 4)])
    content_win.attroff(curses.color_pair(2))

    return content_win


def draw_bar(stdscr: curses.window, y: int, x: int,
             label: str, value: float, width: int = 34) -> None:
    """Draw a horizontal usage bar inside the given window."""

    value = max(0.0, min(value, 100.0))
    filled = int((value / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    color = 3 if value < 80 else 4
    stdscr.attron(curses.color_pair(color))
    stdscr.addstr(y, x, f"{label:<12} [{bar}] {value:5.1f}%")
    stdscr.attroff(curses.color_pair(color))


def draw_section_header(stdscr: curses.window, y: int, text: str) -> None:
    """Render a section header inside the provided window."""

    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(y, 2, text)
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)


def format_bytes(num_bytes: float) -> str:
    """Return a human readable string for a byte value."""

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:6.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:6.1f} PB"