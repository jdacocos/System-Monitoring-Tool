import curses
from collections import deque
import psutil
import time

from frontend.utils.ui_helpers import (
    draw_section_header,
    format_bytes,
    draw_sparkline,
)
from frontend.utils.page_helpers import run_page_loop


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


UPLOAD_HISTORY: deque[float] = deque(maxlen=120)
DOWNLOAD_HISTORY: deque[float] = deque(maxlen=120)


def render_network_stats(
    win: curses.window,
    stats: dict,
    upload_history: deque[float],
    download_history: deque[float],
) -> int:
    """Render upload/download speeds and totals."""

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


def render_network_page(content_win: curses.window) -> None:
    """
    Render Network Monitor page content.
    """
    old_net = getattr(render_network_page, "_prev_net", psutil.net_io_counters())
    old_time = getattr(render_network_page, "_prev_time", time.time())

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

    UPLOAD_HISTORY.append(max(0.0, sent_speed))
    DOWNLOAD_HISTORY.append(max(0.0, recv_speed))

    render_network_page._prev_net = new_net
    render_network_page._prev_time = new_time

    y = 1
    draw_section_header(content_win, y, "Throughput")
    content_win.addstr(y + 1, 2, f"Upload   : {sent_speed:6.2f} MB/s")
    content_win.addstr(y + 2, 2, f"Download : {recv_speed:6.2f} MB/s")
    content_win.addstr(y + 4, 2, f"Total Sent    : {format_bytes(stats['total_sent'])}")
    content_win.addstr(y + 5, 2, f"Total Received: {format_bytes(stats['total_recv'])}")
    draw_sparkline(
        content_win,
        y + 7,
        2,
        list(UPLOAD_HISTORY),
        width=content_win.getmaxyx()[1] - 6,
        label="Upload",
        unit=" MB/s",
    )
    draw_sparkline(
        content_win,
        y + 8,
        2,
        list(DOWNLOAD_HISTORY),
        width=content_win.getmaxyx()[1] - 6,
        label="Download",
        unit=" MB/s",
    )

    # Active interfaces
    draw_section_header(content_win, y + 10, "Active Interfaces")
    for i, (iface, addrs) in enumerate(stats["interfaces"].items()):
        if i >= 4:
            break
        ip_list = [
            addr.address
            for addr in addrs
            if getattr(addr.family, "name", str(addr.family)) in ("AF_INET", "AF_LINK")
        ]
        ip_str = ", ".join(ip_list) or "No address"
        content_win.addstr(y + 11 + i, 4, f"{iface:<10} {ip_str}")


def render_network(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """
    Launch the Network Monitor page loop using the generic `run_page_loop`.
    """
    return run_page_loop(
        stdscr,
        title="Network Monitor",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_network_page,
        sleep_time=0.3,
    )
