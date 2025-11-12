import curses
import os
import platform
import time
import psutil

from utils.ui_helpers import (init_colors, draw_content_window, draw_bar, draw_section_header, format_bytes)
from utils.input_helpers import handle_input, GLOBAL_KEYS


def get_system_stats() -> dict:
    """Fetch CPU, memory, disk, network, and general system statistics."""

    try:
        load_avg = os.getloadavg()
    except (AttributeError, OSError):
        load_avg = (0.0, 0.0, 0.0)

    return {
        "cpu": psutil.cpu_percent(interval=0.1),
        "mem": psutil.virtual_memory(),
        "disk": psutil.disk_usage('/'),
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


def render_resource_bars(win: curses.window, stats: dict) -> None:
    """Render the CPU, memory, and disk usage bars."""

    draw_bar(win, 2, 2, "CPU", stats["cpu"])
    win.addstr(3, 4, f"Cores: {stats['logical_cores']} logical")

    memory = stats["mem"]
    draw_bar(win, 5, 2, "Memory", memory.percent)
    win.addstr(6, 4, f"Used {format_bytes(memory.used)} / {format_bytes(memory.total)}")

    disk = stats["disk"]
    draw_bar(win, 8, 2, "Disk", disk.percent)
    win.addstr(9, 4, f"Used {format_bytes(disk.used)} / {format_bytes(disk.total)}")


def render_network_info(win: curses.window, net) -> None:
    """Display total network usage in MB."""

    sent_mb = net.bytes_sent / (1024 ** 2)
    recv_mb = net.bytes_recv / (1024 ** 2)
    win.addstr(12, 2, f"Upload   : {sent_mb:8.1f} MB")
    win.addstr(13, 2, f"Download : {recv_mb:8.1f} MB")


def render_system_summary(win: curses.window, stats: dict) -> None:
    """Render host summary information safely within window bounds."""
    height, width = win.getmaxyx()

    load1, load5, load15 = stats["load"]
    lines = [
        f"Hostname : {stats['hostname']}",
        f"Uptime   : {format_duration(stats['uptime'])}",
        f"Load Avg : {load1:4.2f} / {load5:4.2f} / {load15:4.2f}",
        f"Processes: {stats['processes']:<5}"
    ]

    start_y = max(1, height - len(lines) - 2)
    for i, text in enumerate(lines):
        if start_y + i < height - 1 and len(text) < width - 2:
            win.addstr(start_y + i, 2, text)


def render_dashboard(stdscr: curses.window,
                     nav_items: list[tuple[str, str, str]],
                     active_page: str) -> int:
    """Render the main dashboard with high level system statistics."""

    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        content_win = draw_content_window(
            stdscr,
            title="System Dashboard",
            nav_items=nav_items,
            active_page=active_page,
        )

        if content_win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.2)
            continue

        stats = get_system_stats()

        draw_section_header(content_win, 1, "Resource Utilization")
        render_resource_bars(content_win, stats)

        draw_section_header(content_win, 11, "Network Activity")
        render_network_info(content_win, stats["net"])

        draw_section_header(content_win, 14, "System Summary")
        render_system_summary(content_win, stats)

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.3)