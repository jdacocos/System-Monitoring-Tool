"""
dashboard_page.py

System dashboard page for the interactive terminal UI.

Shows:
- CPU, memory, and disk resource utilization bars
- Network throughput summary
- Host information, including hostname, uptime, load averages, and process count

Integrates with the generic page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes

Dependencies:
- curses
- os
- platform
- time
- psutil
- frontend.utils.page_helpers
- frontend.utils.ui_helpers
"""

import curses
import os
import platform
import time
import psutil

from frontend.utils.page_helpers import run_page_loop
from frontend.utils.ui_helpers import draw_bar, draw_section_header, format_bytes


def get_system_stats() -> dict:
    """
    Fetch CPU, memory, disk, network, and general system statistics.

    Returns:
        dict: {
            "cpu": float CPU usage percentage,
            "mem": psutil.virtual_memory result,
            "disk": psutil.disk_usage result,
            "net": psutil.net_io_counters result,
            "uptime": float seconds since boot,
            "hostname": str host name,
            "load": tuple of 1, 5, 15 min load averages,
            "processes": int number of active processes,
            "logical_cores": int logical CPU count
        }
    """

    try:
        load_avg = os.getloadavg()
    except (AttributeError, OSError):
        load_avg = (0.0, 0.0, 0.0)

    return {
        "cpu": psutil.cpu_percent(interval=0.1),
        "mem": psutil.virtual_memory(),
        "disk": psutil.disk_usage("/"),
        "net": psutil.net_io_counters(),
        "uptime": time.time() - psutil.boot_time(),
        "hostname": platform.node(),
        "load": load_avg,
        "processes": len(psutil.pids()),
        "logical_cores": psutil.cpu_count(logical=True),
    }


def format_duration(seconds: float) -> str:
    """
    Return a concise uptime string.

    Args:
        seconds (float): Duration in seconds.

    Returns:
        str: Formatted string like '1d 03h 45m' or '03h 45m'.
    """

    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, _ = divmod(seconds, 60)
    if days:
        return f"{days}d {hours:02d}h {minutes:02d}m"
    return f"{hours:02d}h {minutes:02d}m"


def render_dashboard_page(content_win: curses.window) -> None:
    """
    Render the system dashboard page content.

    Displays:
        - Resource utilization bars for CPU, memory, and disk.
        - Network activity summary.
        - System summary information.

    Args:
        content_win (curses.window): Content window from the page loop.
    """

    stats = get_system_stats()

    # Resource bars
    next_y = render_resource_bars(content_win, stats, start_y=1)
    # Network info
    next_y = render_network_info(content_win, stats["net"], start_y=next_y)
    # System summary
    render_system_summary(content_win, stats, start_y=next_y)


def render_resource_bars(win: curses.window, stats: dict, start_y: int) -> int:
    """
    Render CPU, memory, and disk usage bars.

    Args:
        win (curses.window): Window to draw content.
        stats (dict): System statistics dictionary.
        start_y (int): Y-coordinate to start rendering.

    Returns:
        int: Next available y-coordinate after the rendered section.
    """

    draw_section_header(win, start_y, "Resource Utilization")
    y = start_y + 1

    draw_bar(win, y, 2, "CPU", stats["cpu"])
    win.addstr(y + 1, 4, f"Cores: {stats['logical_cores']} logical")

    memory = stats["mem"]
    draw_bar(win, y + 3, 2, "Memory", memory.percent)
    win.addstr(
        y + 4, 4, f"Used {format_bytes(memory.used)} / {format_bytes(memory.total)}"
    )

    disk = stats["disk"]
    draw_bar(win, y + 6, 2, "Disk", disk.percent)
    win.addstr(y + 7, 4, f"Used {format_bytes(disk.used)} / {format_bytes(disk.total)}")

    return y + 9


def render_network_info(win: curses.window, net, start_y: int) -> int:
    """
    Display total network usage in MB.

    Args:
        win (curses.window): Window to draw content.
        net (psutil._common.snetio): Network counters.
        start_y (int): Y-coordinate to start rendering.

    Returns:
        int: Next available y-coordinate after the rendered section.
    """

    draw_section_header(win, start_y, "Network Activity")

    sent_mb = net.bytes_sent / (1024**2)
    recv_mb = net.bytes_recv / (1024**2)
    win.addstr(start_y + 1, 2, f"Upload   : {sent_mb:8.1f} MB")
    win.addstr(start_y + 2, 2, f"Download : {recv_mb:8.1f} MB")

    return start_y + 4


def render_system_summary(win: curses.window, stats: dict, start_y: int) -> None:
    """
    Render host summary information safely within window bounds.

    Args:
        win (curses.window): Window to draw content.
        stats (dict): System statistics dictionary.
        start_y (int): Y-coordinate to start rendering.
    """

    draw_section_header(win, start_y, "System Summary")

    height, width = win.getmaxyx()
    load1, load5, load15 = stats["load"]
    lines = [
        f"Hostname : {stats['hostname']}",
        f"Uptime   : {format_duration(stats['uptime'])}",
        f"Load Avg : {load1:4.2f} / {load5:4.2f} / {load15:4.2f}",
        f"Processes: {stats['processes']:<5}",
    ]

    for i, text in enumerate(lines, start=1):
        if start_y + i >= height - 1:
            break
        win.addstr(start_y + i, 2, text[: max(0, width - 4)])


def render_dashboard(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """
    Launch the System Dashboard page loop using the generic `run_page_loop`.

    Args:
        stdscr (curses.window): Main curses window provided by curses.wrapper.
        nav_items (list[tuple[str, str, str]]): Navigation menu items.
        active_page (str): Currently active page identifier.

    Returns:
        int: Key code of a quit/navigation key if pressed.
    """

    return run_page_loop(
        stdscr,
        title="System Dashboard",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_dashboard_page,
        sleep_time=0.3,
    )
