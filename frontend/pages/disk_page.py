import curses
from collections import deque
import psutil
import time

from frontend.utils.ui_helpers import (
    draw_section_header,
    draw_bar,
    format_bytes,
    draw_sparkline,
)
from frontend.utils.page_helpers import run_page_loop

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


def render_disk_page(content_win: curses.window) -> None:
    """
    Render Disk & I/O Monitor page content.
    """
    # Gather disk usage and I/O stats
    previous_io = getattr(render_disk_page, "_prev_io", None)
    previous_time = getattr(render_disk_page, "_prev_time", time.time())
    if previous_io is None:
        previous_io = psutil.disk_io_counters()
        render_disk_page._prev_io = previous_io

    current_io = psutil.disk_io_counters()
    current_time = time.time()
    elapsed = max(current_time - previous_time, 1e-6)

    read_speed = (current_io.read_bytes - previous_io.read_bytes) / (1024**2) / elapsed
    write_speed = (
        (current_io.write_bytes - previous_io.write_bytes) / (1024**2) / elapsed
    )

    partitions = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
        except (PermissionError, FileNotFoundError, OSError):
            continue
        partitions.append(
            {
                "device": p.device,
                "mountpoint": p.mountpoint,
                "fstype": p.fstype,
                "usage": usage,
            }
        )
    partitions.sort(key=lambda d: d["usage"].percent, reverse=True)

    # Store for next call
    render_disk_page._prev_io = current_io
    render_disk_page._prev_time = current_time

    READ_HISTORY.append(max(0.0, read_speed))
    WRITE_HISTORY.append(max(0.0, write_speed))

    # Draw disk usage
    y = 1
    draw_section_header(content_win, y, "Disk Usage")
    y += 1
    for part in partitions[:4]:
        draw_bar(content_win, y, 2, part["device"][-12:], part["usage"].percent)
        content_win.addstr(
            y + 1,
            4,
            f"{part['mountpoint']} ({part['fstype']}) {format_bytes(part['usage'].used)} / {format_bytes(part['usage'].total)}",
        )
        y += 3

    # Draw I/O speeds
    draw_section_header(content_win, y, "I/O Activity")
    y += 1
    content_win.addstr(y, 2, f"Read  : {read_speed:6.2f} MB/s")
    content_win.addstr(y + 1, 2, f"Write : {write_speed:6.2f} MB/s")
    y += 3
    draw_sparkline(
        content_win,
        y,
        2,
        list(READ_HISTORY),
        width=content_win.getmaxyx()[1] - 6,
        label="Read",
        unit=" MB/s",
    )
    draw_sparkline(
        content_win,
        y + 1,
        2,
        list(WRITE_HISTORY),
        width=content_win.getmaxyx()[1] - 6,
        label="Write",
        unit=" MB/s",
    )


def render_disk(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """
    Launch the Disk Monitor page loop using the generic `run_page_loop`.
    """
    return run_page_loop(
        stdscr,
        title="Disk & I/O Monitor",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_disk_page,
        sleep_time=0.3,
    )
