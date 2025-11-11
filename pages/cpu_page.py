import curses
import psutil
import time
from utils.ui_helpers import init_colors, draw_title, draw_box, draw_footer, draw_bar
from utils.input_helpers import handle_input, GLOBAL_KEYS

# Replace this function with later with our own calculations
def get_cpu_stats() -> dict:
    """Fetch and return key CPU statistics."""
    return {
        "overall": psutil.cpu_percent(interval=0.2),
        "per_core": psutil.cpu_percent(interval=0.2, percpu=True),
        "freq": psutil.cpu_freq(),
        "logical": psutil.cpu_count(logical=True),
        "physical": psutil.cpu_count(logical=False)
    }


def render_overall_cpu(stdscr: curses.window, overall: float,
                       freq, physical: int, logical: int) -> None:
    """Render overall CPU usage and frequency information."""
    stdscr.addstr(2, 4, f"Overall CPU Usage: {overall:>5.1f}%")
    draw_bar(stdscr, 3, 4, "CPU", overall)
    stdscr.addstr(5, 4, f"CPU Frequency: {freq.current:.1f} MHz (min {freq.min:.0f}, max {freq.max:.0f})")
    stdscr.addstr(6, 4, f"Cores: {physical} physical / {logical} logical")


def render_per_core_usage(stdscr: curses.window, per_core: list[float]) -> None:
    """Render per-core CPU usage bars."""
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(8, 4, "Per-Core Usage:")
    stdscr.attroff(curses.color_pair(1))

    for i, core in enumerate(per_core):
        label = f"Core {i + 1:02d}"
        draw_bar(stdscr, 9 + i, 4, label, core)

def render_cpu(stdscr: curses.window) -> int:
    """
    Render the CPU Monitor page.
    Displays overall and per-core CPU usage, frequency, and core count.
    Returns the pressed key for navigation.
    """
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        stdscr.erase()
        stdscr.bkgd(' ', curses.color_pair(1))
        draw_title(stdscr, "CPU MONITOR")
        draw_box(stdscr)

        stats = get_cpu_stats()
        render_overall_cpu(
            stdscr,
            overall=stats["overall"],
            freq=stats["freq"],
            physical=stats["physical"],
            logical=stats["logical"]
        )
        render_per_core_usage(stdscr, stats["per_core"])

        draw_footer(stdscr)
        stdscr.refresh()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.2)