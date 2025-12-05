"""Utility helpers for rendering curses-based user interfaces."""

from __future__ import annotations
import curses
from datetime import datetime
from typing import Iterable, Sequence

# pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals, too-many-statements

SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"

SIDEBAR_WIDTH = 22
MIN_HEIGHT = 22
MIN_WIDTH = 80


def init_colors() -> None:
    """Initialize the color palette used throughout the application."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Header / footer
    curses.init_pair(2, curses.COLOR_CYAN, -1)  # Accent text
    curses.init_pair(3, curses.COLOR_GREEN, -1)  # Healthy metrics
    curses.init_pair(4, curses.COLOR_RED, -1)  # Critical metrics
    curses.init_pair(5, curses.COLOR_WHITE, -1)  # Default text
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Active navigation
    curses.init_pair(7, curses.COLOR_BLUE, -1)  # Sidebar text


def draw_header(stdscr: curses.window, title: str) -> None:
    """Render the top header banner with a dynamically updating timestamp."""
    _, width = stdscr.getmaxyx()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.hline(0, 0, " ", width)
    stdscr.addstr(0, 2, title[: max(0, width - 4)])
    stdscr.addstr(0, max(2, width - len(timestamp) - 2), timestamp)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)


def draw_sidebar(
    stdscr: curses.window, nav_items: Sequence[tuple[str, str, str]], active_page: str
) -> None:
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
        display = f"[{key.upper()}] {label:<12}"[: SIDEBAR_WIDTH - 2]
        attr = curses.color_pair(6) if page_id == active_page else curses.color_pair(5)
        stdscr.attron(attr)
        stdscr.addstr(y, 1, display.ljust(SIDEBAR_WIDTH - 2))
        stdscr.attroff(attr)

    for y in range(1, height - 1):
        stdscr.addch(y, SIDEBAR_WIDTH - 1, curses.ACS_VLINE)


def draw_footer(
    stdscr: curses.window, nav_items: Iterable[tuple[str, str, str]]
) -> None:
    """Render a footer with contextual key bindings."""
    height, width = stdscr.getmaxyx()
    instructions = (
        "  ".join(f"[{key}] {label}" for _, label, key in nav_items) + "  [q] Quit"
    )

    stdscr.attron(curses.color_pair(1))
    stdscr.hline(height - 1, 0, " ", width)
    # stdscr.attron(curses.A_BOLD)
    stdscr.addstr(height - 1, 2, instructions[: max(0, width - 4)])
    # stdscr.attroff(curses.A_BOLD)
    stdscr.attroff(curses.color_pair(1))


def draw_content_window(
    stdscr: curses.window,
    title: str,
    nav_items: Sequence[tuple[str, str, str]],
    active_page: str,
) -> curses.window | None:
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
            height // 2, max(0, (width - len(msg)) // 2), msg[: max(0, width - 2)]
        )
        stdscr.refresh()
        return None

    stdscr.erase()
    stdscr.bkgd(" ", curses.color_pair(5))
    draw_header(stdscr, title)
    draw_sidebar(stdscr, nav_items, active_page)
    draw_footer(stdscr, nav_items)

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


def draw_bar(
    stdscr: curses.window, y: int, x: int, label: str, value: float, width: int = 34
) -> None:
    """Draw a horizontal usage bar inside the given window."""
    value = max(0.0, min(value, 100.0))
    filled = int((value / 100) * width)
    bar_str = "█" * filled + "░" * (width - filled)
    color = 3 if value < 80 else 4
    stdscr.attron(curses.color_pair(color))
    stdscr.addstr(y, x, f"{label:<12} [{bar_str}] {value:5.1f}%")
    stdscr.attroff(curses.color_pair(color))


def draw_section_header(stdscr: curses.window, y: int, text: str) -> None:
    """Render a section header inside the provided window."""
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(y, 2, text)
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)


def draw_sparkline(
    stdscr: curses.window,
    y: int,
    x: int,
    data: Sequence[float],
    width: int,
    label: str,
    unit: str = "",
    color_pair: int = 2,
    fixed_min: float | None = None,
    fixed_max: float | None = None,
) -> None:
    """Render a simple one-line sparkline graph for recent samples."""
    if not data or width <= 0:
        return

    height, total_width = stdscr.getmaxyx()
    if y >= height - 1 or x >= total_width - 1:
        return

    label_field = f"{label:<12}"
    graph_start = x + len(label_field)
    max_width = max(1, min(width, total_width - graph_start - 12))
    samples = data[-max_width:]

    minimum = fixed_min if fixed_min is not None else min(samples)
    maximum = fixed_max if fixed_max is not None else max(samples)
    if maximum - minimum < 1e-6:
        maximum = minimum + 1e-6

    levels = len(SPARKLINE_CHARS) - 1
    spark_chars = [
        SPARKLINE_CHARS[
            int(min(levels, max(0, (value - minimum) / (maximum - minimum) * levels)))
        ]
        for value in samples
    ]

    sparkline = "".join(spark_chars).rjust(max_width)
    value_text = f"{samples[-1]:6.2f}{unit}"

    stdscr.attron(curses.color_pair(color_pair) | curses.A_BOLD)
    stdscr.addstr(y, x, label_field)
    stdscr.attroff(curses.color_pair(color_pair) | curses.A_BOLD)

    stdscr.addstr(y, graph_start, " " * max_width)
    stdscr.addstr(y, graph_start, sparkline[:max_width])

    value_start = min(total_width - len(value_text) - 1, graph_start + max_width + 1)
    value_start = max(graph_start + 1, value_start)
    if value_start < total_width - 1:
        truncated = value_text[: max(0, total_width - value_start - 1)]
        stdscr.addstr(y, value_start, truncated)


def format_bytes(num_bytes: float) -> str:
    """Return a human readable string for a byte value."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:6.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:6.1f} PB"
