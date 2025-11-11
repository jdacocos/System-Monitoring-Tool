import curses
import psutil
import time
from utils.ui_helpers import init_colors, draw_title, draw_box, draw_bar, draw_footer
from utils.input_helpers import handle_input, GLOBAL_KEYS

# Replace this function with later with our own calculations
def get_system_stats() -> dict:
    """Fetch CPU, memory, disk, and network statistics."""
    return {
        "cpu": psutil.cpu_percent(interval=0.2),
        "mem": psutil.virtual_memory(),
        "disk": psutil.disk_usage('/'),
        "net": psutil.net_io_counters()
    }

def render_resource_bars(stdscr: curses.window, stats: dict) -> None:
    """Render the CPU, memory, and disk usage bars."""
    draw_bar(stdscr, 3, 4, "CPU", stats["cpu"])
    draw_bar(stdscr, 5, 4, "Memory", stats["mem"].percent)
    draw_bar(stdscr, 7, 4, "Disk", stats["disk"].percent)

def render_network_info(stdscr: curses.window, net) -> None:
    """Display total network usage in MB."""
    sent_mb = net.bytes_sent / (1024 ** 2)
    recv_mb = net.bytes_recv / (1024 ** 2)
    stdscr.addstr(9, 4, f"Network: Sent {sent_mb:8.1f} MB | Received {recv_mb:8.1f} MB")

def render_dashboard(stdscr: curses.window) -> int:
    """
    Render the main system dashboard with CPU, Memory, Disk, and Network stats.
    Returns the pressed key for navigation.
    """
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        stdscr.erase()
        stdscr.bkgd(' ', curses.color_pair(1))
        draw_title(stdscr, "SYSTEM MONITORING DASHBOARD")
        draw_box(stdscr)

        stats = get_system_stats()
        render_resource_bars(stdscr, stats)
        render_network_info(stdscr, stats["net"])

        draw_footer(stdscr)
        stdscr.refresh()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.2)
