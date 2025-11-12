import curses
import psutil
import time

from utils.ui_helpers import (init_colors, draw_content_window, draw_section_header, format_bytes)

from utils.input_helpers import handle_input, GLOBAL_KEYS

# Replace this function with later with our own calculations
def get_network_stats(old_net, old_time: float) -> tuple[dict, psutil._common.snetio, float]:
    """Fetch network stats and calculate upload/download speeds."""
    new_net = psutil.net_io_counters()
    new_time = time.time()
    elapsed = new_time - old_time

    sent_speed = (new_net.bytes_sent - old_net.bytes_sent) / (1024 ** 2) / elapsed
    recv_speed = (new_net.bytes_recv - old_net.bytes_recv) / (1024 ** 2) / elapsed

    stats = {
        "sent_speed": sent_speed,
        "recv_speed": recv_speed,
        "total_sent": new_net.bytes_sent,
        "total_recv": new_net.bytes_recv,
        "interfaces": psutil.net_if_addrs()
    }

    return stats, new_net, new_time


def render_network_stats(win: curses.window, stats: dict) -> None:
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


def render_active_interfaces(win: curses.window, interfaces: dict) -> None:
    """Display up to four active network interfaces with their IP addresses."""

    draw_section_header(win, 8, "Active Interfaces")

    for i, (iface, addrs) in enumerate(interfaces.items()):
        if i >= 5:
            break

        ip_list = [
            addr.address
            for addr in addrs
            if getattr(addr.family, "name", str(addr.family)) in ("AF_INET", "AF_LINK", "AddressFamily.AF_INET")
        ]
        ip_str = ", ".join(ip_list) or "No address"
        win.addstr(9 + i, 4, f"{iface:<10} {ip_str}")


def render_network(stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str) -> int:
    """Render the Network Monitor page."""

    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    old_net = psutil.net_io_counters()
    old_time = time.time()

    while True:
        content_win = draw_content_window(stdscr, title="Network Monitor", nav_items=nav_items, active_page=active_page)

        if content_win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.2)
            continue

        stats, old_net, old_time = get_network_stats(old_net, old_time)
        render_network_stats(content_win, stats)
        render_active_interfaces(content_win, stats["interfaces"])

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.3)