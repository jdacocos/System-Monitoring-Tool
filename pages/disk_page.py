import curses
from collections import deque
import psutil
import time

from utils.ui_helpers import (
    init_colors,
    draw_content_window,
    draw_section_header,
    draw_bar,
    format_bytes,
    draw_sparkline,
)
from utils.input_helpers import handle_input, GLOBAL_KEYS

READ_HISTORY: deque[float] = deque(maxlen=120)
WRITE_HISTORY: deque[float] = deque(maxlen=120)


def get_disk_stats(
    previous_io: psutil._common.sdiskio | None, previous_time: float
) -> tuple[dict, psutil._common.sdiskio, float]:
    """Collect disk usage, partition details, and I/O throughput."""

    if previous_io is None:
        previous_io = psutil.disk_io_counters()
        previous_time = time.time()

    current_io = psutil.disk_io_counters()
    current_time = time.time()
    elapsed = max(current_time - previous_time, 1e-6)

    read_speed = (current_io.read_bytes - previous_io.read_bytes) / (1024**2) / elapsed
    write_speed = (
        (current_io.write_bytes - previous_io.write_bytes) / (1024**2) / elapsed
    )

    partitions: list[dict] = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except (PermissionError, FileNotFoundError, OSError):
            continue
        partitions.append(
            {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "usage": usage,
            }
        )

    partitions.sort(key=lambda item: item["usage"].percent, reverse=True)

    stats = {
        "read_speed": max(0.0, read_speed),
        "write_speed": max(0.0, write_speed),
        "total_read": current_io.read_bytes,
        "total_write": current_io.write_bytes,
        "partitions": partitions,
    }

    return stats, current_io, current_time


def render_disk_usage(win: curses.window, partitions: list[dict], start_y: int) -> int:
    """Render a set of disk usage bars for mounted partitions."""

    draw_section_header(win, start_y, "Disk Usage")
    y = start_y + 1
    width = win.getmaxyx()[1] - 6

    if not partitions:
        win.addstr(y, 2, "No mounted partitions accessible.")
        return y + 2

    for partition in partitions[:4]:
        label = partition["device"][-12:]
        usage = partition["usage"]
        draw_bar(win, y, 2, label, usage.percent)
        info = (
            f"{partition['mountpoint']} ({partition['fstype'] or 'unknown'}) "
            f"{format_bytes(usage.used).strip()} / {format_bytes(usage.total).strip()}"
        )
        win.addstr(y + 1, 4, info[: max(0, width)])
        y += 3

    return y


def render_disk_io(
    win: curses.window,
    stats: dict,
    read_history: deque[float],
    write_history: deque[float],
    start_y: int,
) -> None:
    """Render current disk I/O speeds with historical sparklines."""

    draw_section_header(win, start_y, "I/O Activity")

    read_color = 3 if stats["read_speed"] < 50 else 4
    write_color = 3 if stats["write_speed"] < 50 else 4

    win.attron(curses.color_pair(read_color))
    win.addstr(start_y + 1, 2, f"Read  : {stats['read_speed']:6.2f} MB/s")
    win.attroff(curses.color_pair(read_color))

    win.attron(curses.color_pair(write_color))
    win.addstr(start_y + 2, 2, f"Write : {stats['write_speed']:6.2f} MB/s")
    win.attroff(curses.color_pair(write_color))

    win.addstr(start_y + 4, 2, f"Total Read : {format_bytes(stats['total_read'])}")
    win.addstr(start_y + 5, 2, f"Total Write: {format_bytes(stats['total_write'])}")

    width = win.getmaxyx()[1] - 6
    draw_sparkline(
        win, start_y + 7, 2, list(read_history), width=width, label="Read", unit=" MB/s"
    )
    draw_sparkline(
        win,
        start_y + 8,
        2,
        list(write_history),
        width=width,
        label="Write",
        unit=" MB/s",
    )


def render_disk(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """Render the disk usage and I/O monitoring page."""

    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    previous_io = psutil.disk_io_counters()
    previous_time = time.time()

    while True:
        content_win = draw_content_window(
            stdscr,
            title="Disk & I/O Monitor",
            nav_items=nav_items,
            active_page=active_page,
        )

        if content_win is None:
            key = handle_input(stdscr, GLOBAL_KEYS)
            if key != -1:
                return key
            time.sleep(0.2)
            continue

        stats, previous_io, previous_time = get_disk_stats(previous_io, previous_time)
        READ_HISTORY.append(stats["read_speed"])
        WRITE_HISTORY.append(stats["write_speed"])

        next_y = render_disk_usage(content_win, stats["partitions"], start_y=1)
        render_disk_io(content_win, stats, READ_HISTORY, WRITE_HISTORY, start_y=next_y)

        content_win.noutrefresh()
        stdscr.noutrefresh()
        curses.doupdate()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.3)
