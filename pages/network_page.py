import curses
import psutil
import time
from utils.ui_helpers import init_colors, draw_title, draw_box, draw_footer
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
        "total_sent": new_net.bytes_sent / (1024 ** 2),
        "total_recv": new_net.bytes_recv / (1024 ** 2),
        "interfaces": psutil.net_if_addrs()
    }

    return stats, new_net, new_time


def render_network_stats(stdscr: curses.window, stats: dict) -> None:
    """Render upload/download speeds and totals."""
    color_sent = 3 if stats["sent_speed"] < 5 else 4
    color_recv = 3 if stats["recv_speed"] < 5 else 4

    stdscr.addstr(2, 4, "Network Usage")

    stdscr.attron(curses.color_pair(color_sent))
    stdscr.addstr(4, 4, f"Upload Speed:   {stats['sent_speed']:6.2f} MB/s")
    stdscr.attroff(curses.color_pair(color_sent))

    stdscr.attron(curses.color_pair(color_recv))
    stdscr.addstr(5, 4, f"Download Speed: {stats['recv_speed']:6.2f} MB/s")
    stdscr.attroff(curses.color_pair(color_recv))

    stdscr.addstr(7, 4, f"Total Sent:     {stats['total_sent']:8.1f} MB")
    stdscr.addstr(8, 4, f"Total Received: {stats['total_recv']:8.1f} MB")


def render_active_interfaces(stdscr: curses.window, interfaces: dict) -> None:
    """Display up to four active network interfaces with their IP addresses."""
    stdscr.addstr(10, 4, "Active Interfaces:")

    for i, (iface, addrs) in enumerate(interfaces.items()):
        if i >= 4:
            break

        ip_list = [addr.address for addr in addrs if addr.family.name in ("AF_INET", "AF_LINK")]
        ip_str = ", ".join(ip_list)
        stdscr.addstr(11 + i, 6, f"{iface:<10} {ip_str}")


def render_network(stdscr: curses.window) -> int:
    """
    Render the Network Monitor page.
    Displays upload/download speeds, total data, and active interfaces.
    Returns the pressed key for navigation.
    """
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    old_net = psutil.net_io_counters()
    old_time = time.time()

    while True:
        stdscr.erase()
        stdscr.bkgd(' ', curses.color_pair(1))
        draw_title(stdscr, "NETWORK MONITOR")
        draw_box(stdscr)

        stats, old_net, old_time = get_network_stats(old_net, old_time)
        render_network_stats(stdscr, stats)
        render_active_interfaces(stdscr, stats["interfaces"])

        draw_footer(stdscr)
        stdscr.refresh()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.3)
