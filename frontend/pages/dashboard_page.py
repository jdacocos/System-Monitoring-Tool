import curses
import os
import platform
import time
import psutil

from frontend.utils.ui_helpers import (
    draw_bar,
    draw_section_header,
    format_bytes,
)
from frontend.utils.page_helpers import run_page_loop


def get_system_stats() -> dict:
    """Fetch CPU, memory, disk, network, and general system statistics."""

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
    """Return a concise uptime string."""

    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, _ = divmod(seconds, 60)
    if days:
        return f"{days}d {hours:02d}h {minutes:02d}m"
    return f"{hours:02d}h {minutes:02d}m"


def render_resource_bars(win: curses.window, stats: dict, start_y: int) -> int:
    """Render the CPU, memory, and disk usage bars."""

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
    """Display total network usage in MB."""

    draw_section_header(win, start_y, "Network Activity")

    sent_mb = net.bytes_sent / (1024**2)
    recv_mb = net.bytes_recv / (1024**2)
    win.addstr(start_y + 1, 2, f"Upload   : {sent_mb:8.1f} MB")
    win.addstr(start_y + 2, 2, f"Download : {recv_mb:8.1f} MB")

    return start_y + 4


def render_system_summary(win: curses.window, stats: dict, start_y: int) -> None:
    """Render host summary information safely within window bounds."""

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
    """
    return run_page_loop(
        stdscr,
        title="System Dashboard",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_dashboard_page,
        sleep_time=0.3,
    )
