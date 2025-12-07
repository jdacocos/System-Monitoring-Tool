"""
cpu_page.py

CPU monitoring page for the interactive terminal UI.

Shows:
- Overall and per-core CPU usage in real-time
- CPU percentage per core and overall
- CPU frequency information (current, min, max)
- Logical and physical core counts
- Usage trends over time via sparklines

Integrates with the generic page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes

Dependencies:
- curses
- collections.deque
- frontend.utils.ui_helpers
- frontend.utils.page_helpers
- backend.cpu_info
"""

import curses
from collections import deque

from frontend.utils.ui_helpers import (
    draw_bar,
    draw_section_header,
    draw_sparkline,
)
from frontend.utils.page_helpers import run_page_loop
from backend.cpu_info import (
    get_cpu_percent_per_core,
    get_cpu_freq,
    get_logical_cpu_count,
    get_physical_cpu_count,
)

# Maintain history of overall CPU usage for trend sparklines
CPU_HISTORY: deque[float] = deque(maxlen=120)


def get_cpu_stats() -> dict:
    """
    Fetch and return key CPU statistics.

    Returns:
        dict: {
            "overall": overall CPU usage percentage,
            "per_core": list of per-core CPU usage percentages,
            "freq": CPU frequency info object or None,
            "logical": number of logical CPUs,
            "physical": number of physical cores
        }
    """

    per_core = get_cpu_percent_per_core(interval=0.1)
    overall = sum(per_core) / len(per_core) if per_core else 0.0
    freq = get_cpu_freq()
    return {
        "overall": overall,
        "per_core": per_core,
        "freq": freq,
        "logical": get_logical_cpu_count(),
        "physical": get_physical_cpu_count(),
    }


def render_overall_cpu(win: curses.window, stats: dict, history: deque[float]) -> int:
    """
    Render overall CPU usage and frequency information.

    Parameters:
        win (curses.window): Window to draw content.
        stats (dict): CPU stats dictionary returned by get_cpu_stats().
        history (deque): Historical CPU usage values for sparklines.

    Returns:
        int: The y-coordinate below the rendered section.
    """

    freq = stats["freq"]
    draw_section_header(win, 1, "Overall CPU")
    draw_bar(win, 2, 2, "Usage", stats["overall"])

    if freq is not None:
        win.addstr(
            3,
            4,
            f"Frequency: {freq.current:6.1f} MHz (min {freq.min:.0f}, max {freq.max:.0f})",
        )
    else:
        win.addstr(3, 4, "Frequency information unavailable")

    win.addstr(
        4, 4, f"Cores: {stats['physical']} physical / {stats['logical']} logical"
    )

    width = win.getmaxyx()[1] - 6
    draw_sparkline(
        win,
        5,
        2,
        list(history),
        width=width,
        label="Trend",
        unit="%",
        fixed_min=0.0,
        fixed_max=100.0,
    )

    return 7


def _compute_core_layout(win: curses.window) -> dict:
    """
    Helper:
    Compute layout parameters for per-core CPU display.

    Parameters:
        win (curses.window): Window to draw content.

    Returns:
        dict: Layout configuration including 'height', 'cols', 'column_width',
              and 'bar_width'.
    """

    height, width = win.getmaxyx()
    available_width = max(24, width - 4)

    column_width = 28
    cols = max(1, available_width // column_width)
    bar_width = max(10, column_width - 14)

    return {
        "height": height,
        "cols": cols,
        "column_width": column_width,
        "bar_width": bar_width,
    }


def _render_single_core(
    win: curses.window,
    layout: dict,
    core_index: int,
    usage_value: float,
    start_y: int,
) -> bool:
    """
    Helper:
    Render a single per-core usage bar.

    Parameters:
        win (curses.window): Window to draw content.
        layout (dict): Layout dictionary from _compute_core_layout().
        core_index (int): Index of the CPU core.
        usage_value (float): CPU usage percentage for this core.
        start_y (int): Starting y-coordinate for rendering.

    Returns:
        bool: False if rendering exceeds available screen space; True otherwise.
    """

    row = core_index // layout["cols"]
    col = core_index % layout["cols"]

    y = start_y + row * 2
    x = 2 + col * layout["column_width"]

    if y >= layout["height"] - 2:
        return False  # Stop rendering if there's no space

    label = f"Core {core_index + 1:02d}"
    draw_bar(win, y, x, label, usage_value, width=layout["bar_width"])
    return True


def render_per_core_usage(
    win: curses.window, per_core: list[float], start_y: int = 8
) -> None:
    """
    Render per-core CPU usage bars in a responsive grid.

    Parameters:
        win (curses.window): Window to draw content.
        per_core (list[float]): List of per-core CPU usage percentages.
        start_y (int, optional): Y-coordinate to start rendering. Defaults to 8.
    """

    draw_section_header(win, start_y - 1, "Per-Core Usage")

    layout = _compute_core_layout(win)

    for index, value in enumerate(per_core):
        if not _render_single_core(win, layout, index, value, start_y):
            break


def render_cpu_page(content_win: curses.window) -> None:
    """
    Render the CPU monitoring page content.

    Parameters:
        content_win (curses.window): Content window from the page loop.
    """

    stats = get_cpu_stats()
    CPU_HISTORY.append(stats["overall"])

    # Render overall CPU usage and frequency
    next_y = render_overall_cpu(content_win, stats, CPU_HISTORY)

    # Render per-core usage bars starting below the overall stats
    render_per_core_usage(content_win, stats["per_core"], start_y=next_y)


def render_cpu(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """
    Launch the CPU Monitor page loop.

    Parameters:
        stdscr (curses.window): Main curses window from curses.wrapper.
        nav_items (list[tuple[str, str, str]]): Navigation menu items.
        active_page (str): Currently active page identifier.

    Returns:
        int: Key pressed to exit or switch pages.
    """

    return run_page_loop(
        stdscr,
        title="CPU Monitor",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_cpu_page,
        sleep_time=0.3,
    )
