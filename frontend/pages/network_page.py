"""
network_page.py

Network monitoring page for the interactive terminal UI.

Provides real-time information on:
- Upload and download speeds (MB/s)
- Total bytes sent and received
- Historical throughput trends via sparklines
- Active network interfaces with their IP addresses

Integrates with the generic page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes
"""

import curses
import time
from collections import deque
import psutil

from frontend.utils.ui_helpers import (
    draw_section_header,
    format_bytes,
    draw_sparkline,
)
from frontend.utils.page_helpers import run_page_loop

# Globals for network history
upload_history: deque[float] = deque(maxlen=120)
download_history: deque[float] = deque(maxlen=120)


# Replace this function with later with our own calculations
def get_network_stats(
    old_net, old_time: float
) -> tuple[dict, psutil._common.snetio, float]:
    """Fetch network stats and calculate upload/download speeds."""
    new_net = psutil.net_io_counters()
    new_time = time.time()
    elapsed = new_time - old_time

    sent_speed = (new_net.bytes_sent - old_net.bytes_sent) / (1024**2) / elapsed
    recv_speed = (new_net.bytes_recv - old_net.bytes_recv) / (1024**2) / elapsed

    stats = {
        "sent_speed": sent_speed,
        "recv_speed": recv_speed,
        "total_sent": new_net.bytes_sent,
        "total_recv": new_net.bytes_recv,
        "interfaces": psutil.net_if_addrs(),
    }

    return stats, new_net, new_time


def render_network_stats(win: curses.window, stats: dict) -> int:
    """Render upload/download speeds and totals using module-level history."""

    draw_section_header(win, 1, "Throughput")
    color_sent = 3 if stats["sent_speed"] < 5 else 4
    color_recv = 3 if stats["recv_speed"] < 5 else 4

    win.attron(curses.color_pair(color_sent))
    win.addstr(2, 2, f"Upload   : {stats['sent_speed']:6.2f} MB/s")
    win.attroff(curses.color_pair(color_sent))

    win.attron(curses.color_pair(color_recv))
    win.addstr(3, 2, f"Download : {stats['recv_speed']:6.2f} MB/s")
    win.attroff(curses.color_pair(color_recv))

    win.addstr(5, 2, f"Total Sent    : {format_bytes(stats['total_sent'])}")
    win.addstr(6, 2, f"Total Received: {format_bytes(stats['total_recv'])}")

    width = win.getmaxyx()[1] - 6
    draw_sparkline(
        win, 8, 2, list(upload_history), width=width, label="Upload", unit=" MB/s"
    )
    draw_sparkline(
        win, 9, 2, list(download_history), width=width, label="Download", unit=" MB/s"
    )

    return 11


def render_active_interfaces(
    win: curses.window, interfaces: dict, start_y: int
) -> None:
    """Display up to four active network interfaces with their IP addresses."""

    draw_section_header(win, start_y, "Active Interfaces")

    for i, (iface, addrs) in enumerate(interfaces.items()):
        if i >= 5:
            break

        ip_list = [
            addr.address
            for addr in addrs
            if getattr(addr.family, "name", str(addr.family))
            in ("AF_INET", "AF_LINK", "AddressFamily.AF_INET")
        ]
        ip_str = ", ".join(ip_list) or "No address"
        win.addstr(start_y + 1 + i, 4, f"{iface:<10} {ip_str}")


def _calculate_network_speeds(
    old_net, old_time: float
) -> tuple[dict, psutil._common.snetio, float]:
    """Calculate upload/download speeds and return updated stats."""
    new_net = psutil.net_io_counters()
    new_time = time.time()
    elapsed = max(new_time - old_time, 1e-6)

    sent_speed = (new_net.bytes_sent - old_net.bytes_sent) / (1024**2) / elapsed
    recv_speed = (new_net.bytes_recv - old_net.bytes_recv) / (1024**2) / elapsed

    stats = {
        "sent_speed": sent_speed,
        "recv_speed": recv_speed,
        "total_sent": new_net.bytes_sent,
        "total_recv": new_net.bytes_recv,
        "interfaces": psutil.net_if_addrs(),
    }

    return stats, new_net, new_time


def _render_throughput(win: curses.window, stats: dict) -> int:
    """Render upload/download speeds and totals."""
    draw_section_header(win, 1, "Throughput")
    win.addstr(2, 2, f"Upload   : {stats['sent_speed']:6.2f} MB/s")
    win.addstr(3, 2, f"Download : {stats['recv_speed']:6.2f} MB/s")
    win.addstr(5, 2, f"Total Sent    : {format_bytes(stats['total_sent'])}")
    win.addstr(6, 2, f"Total Received: {format_bytes(stats['total_recv'])}")

    width = win.getmaxyx()[1] - 6
    draw_sparkline(
        win, 8, 2, list(upload_history), width=width, label="Upload", unit=" MB/s"
    )
    draw_sparkline(
        win, 9, 2, list(download_history), width=width, label="Download", unit=" MB/s"
    )

    return 11


def _render_interfaces(win: curses.window, interfaces: dict, start_y: int) -> None:
    """Render up to four active network interfaces with IP addresses."""
    draw_section_header(win, start_y, "Active Interfaces")

    for i, (iface, addrs) in enumerate(interfaces.items()):
        if i >= 4:
            break
        ip_list = [
            addr.address
            for addr in addrs
            if getattr(addr.family, "name", str(addr.family)) in ("AF_INET", "AF_LINK")
        ]
        ip_str = ", ".join(ip_list) or "No address"
        win.addstr(start_y + 1 + i, 4, f"{iface:<10} {ip_str}")


def render_network_page(content_win: curses.window) -> None:
    """
    Render Network Monitor page content.

    Uses private helpers to calculate speeds and draw throughput and interfaces.
    """
    old_net = getattr(render_network_page, "prev_net", psutil.net_io_counters())
    old_time = getattr(render_network_page, "prev_time", time.time())

    stats, new_net, new_time = _calculate_network_speeds(old_net, old_time)

    upload_history.append(max(0.0, stats["sent_speed"]))
    download_history.append(max(0.0, stats["recv_speed"]))

    render_network_page.prev_net = new_net
    render_network_page.prev_time = new_time

    next_y = _render_throughput(content_win, stats)
    _render_interfaces(content_win, stats["interfaces"], start_y=next_y)


def render_network(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """Launch the Network Monitor page loop using the generic `run_page_loop`."""
    return run_page_loop(
        stdscr,
        title="Network Monitor",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_network_page,
        sleep_time=0.3,
    )
