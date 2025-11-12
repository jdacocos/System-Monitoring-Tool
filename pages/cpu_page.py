import curses
import psutil
import time

from utils.ui_helpers import (init_colors, draw_content_window, draw_bar, draw_section_header)
from utils.input_helpers import handle_input, GLOBAL_KEYS


def get_cpu_stats() -> dict:
    """Fetch and return key CPU statistics."""

    per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    overall = sum(per_core) / len(per_core) if per_core else 0.0
    freq = psutil.cpu_freq()
    return {
        "overall": overall,
        "per_core": per_core,
        "freq": freq,
        "logical": psutil.cpu_count(logical=True),
        "physical": psutil.cpu_count(logical=False),
    }


def render_overall_cpu(win: curses.window, stats: dict) -> None:
    """Render overall CPU usage and frequency information."""

    freq = stats["freq"]
    draw_section_header(win, 1, "Overall CPU")
    draw_bar(win, 2, 2, "Usage", stats["overall"])

    if freq is not None:
        win.addstr(3, 4, f"Frequency: {freq.current:6.1f} MHz (min {freq.min:.0f}, max {freq.max:.0f})")
    else:
        win.addstr(3, 4, "Frequency information unavailable")

    win.addstr(4, 4, f"Cores: {stats['physical']} physical / {stats['logical']} logical")


def render_per_core_usage(win: curses.window, per_core: list[float]) -> None:
    """Render per-core CPU usage bars in a responsive grid."""

    draw_section_header(win, 6, "Per-Core Usage")

    height, width = win.getmaxyx()
    available_width = max(24, width - 4)
    column_width = 28
    cols = max(1, available_width // column_width)
    bar_width = max(10, column_width - 14)

    start_y = 7
    for index, value in enumerate(per_core):
        row = index // cols
        col = index % cols
        y = start_y + row * 2
        x = 2 + col * column_width

        if y >= height - 2:
            break

        label = f"Core {index + 1:02d}"
        draw_bar(win, y, x, label, value, width=bar_width)


def render_cpu(stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str) -> int:
    """Render the CPU monitor page."""

    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        content_win = draw_content_window(stdscr, title="CPU Monitor", nav_items=nav_items, active_page=active_page)

        if content_win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.2)
            continue

        stats = get_cpu_stats()
        render_overall_cpu(content_win, stats)
        render_per_core_usage(content_win, stats["per_core"])

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.3)