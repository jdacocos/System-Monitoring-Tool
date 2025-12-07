"""
disk_page.py

Disk monitoring page for the interactive terminal UI.

Shows:
- Disk usage for mounted partitions with visual usage bars
- Real-time disk I/O throughput (read/write speeds)
- Total read and write amounts
- Historical trends via sparklines for read/write speeds

Integrates with the generic page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes

Dependencies:
- curses
- time
- collections.deque
- psutil
- frontend.utils.ui_helpers
- frontend.utils.page_helpers
"""

import curses
import time
from collections import deque
import psutil

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
    """
    Collect disk usage, partition details, and I/O throughput.

    Args:
        previous_io (sdiskio | None): Previous I/O counters.
        previous_time (float): Timestamp of previous counters.

    Returns:
        tuple[dict, sdiskio, float]: Disk stats, current I/O counters, timestamp
    """

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
    """
    Render a set of disk usage bars for mounted partitions.

    Args:
        win (curses.window): Window to draw on.
        partitions (list[dict]): List of partition info.
        start_y (int): Starting y-coordinate.

    Returns:
        int: Updated y-coordinate after rendering.
    """

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
    """
    Render current disk I/O speeds with historical sparklines.

    Args:
        win (curses.window): Window to draw on.
        stats (dict): Disk stats containing read/write speeds and totals.
        read_history (deque[float]): Historical read speeds.
        write_history (deque[float]): Historical write speeds.
        start_y (int): Starting y-coordinate.
    """

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


def _collect_io_stats() -> tuple[float, float]:
    """
    Helper:
    Collect disk I/O stats and compute read/write speeds (MB/s).

    Returns:
        tuple[float, float]: Current read and write speeds.
    """

    prev_io = getattr(_collect_io_stats, "prev_io", None)
    prev_time = getattr(_collect_io_stats, "prev_time", time.time())

    if prev_io is None:
        prev_io = psutil.disk_io_counters()
        _collect_io_stats.prev_io = prev_io

    current_io = psutil.disk_io_counters()
    current_time = time.time()
    elapsed = max(current_time - prev_time, 1e-6)

    read_speed = (current_io.read_bytes - prev_io.read_bytes) / (1024**2) / elapsed
    write_speed = (current_io.write_bytes - prev_io.write_bytes) / (1024**2) / elapsed

    # Save state for next tick
    _collect_io_stats.prev_io = current_io
    _collect_io_stats.prev_time = current_time

    return read_speed, write_speed


def _collect_partitions() -> list[dict]:
    """
    Helper:
    Collect mounted partitions and usage info.

    Returns:
        list[dict]: Top 4 partitions sorted by usage percentage.
    """

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
    return partitions[:4]  # We only display the top 4


def _render_disk_usage(
    content_win: curses.window, y: int, partitions: list[dict]
) -> int:
    """
    Helper:
    Render the Disk Usage section and return the updated y position.

    Args:
        content_win (curses.window): Window to draw on.
        y (int): Starting y-coordinate.
        partitions (list[dict]): List of partitions.

    Returns:
        int: Updated y-coordinate.
    """

    draw_section_header(content_win, y, "Disk Usage")
    y += 1

    for part in partitions:
        draw_bar(content_win, y, 2, part["device"][-12:], part["usage"].percent)
        content_win.addstr(
            y + 1,
            4,
            f"{part['mountpoint']} ({part['fstype']})  "
            f"{format_bytes(part['usage'].used)} / {format_bytes(part['usage'].total)}",
        )
        y += 3

    return y


def _render_io_activity(
    content_win: curses.window,
    y: int,
    read_speed: float,
    write_speed: float,
) -> None:
    """
    Helper:
    Render the I/O speeds and historical sparklines.

    Args:
        content_win (curses.window): Window to draw on.
        y (int): Starting y-coordinate.
        read_speed (float): Current read speed in MB/s.
        write_speed (float): Current write speed in MB/s.
    """

    draw_section_header(content_win, y, "I/O Activity")
    y += 1

    content_win.addstr(y, 2, f"Read  : {read_speed:6.2f} MB/s")
    content_win.addstr(y + 1, 2, f"Write : {write_speed:6.2f} MB/s")
    y += 3

    width = content_win.getmaxyx()[1] - 6

    draw_sparkline(
        content_win, y, 2, list(READ_HISTORY), width=width, label="Read", unit=" MB/s"
    )
    draw_sparkline(
        content_win,
        y + 1,
        2,
        list(WRITE_HISTORY),
        width=width,
        label="Write",
        unit=" MB/s",
    )


def render_disk_page(content_win: curses.window) -> None:
    """
    Render the Disk & I/O monitor page content.

    Args:
        content_win (curses.window): Window to draw page content.
    """

    # 1. Collect stats
    read_speed, write_speed = _collect_io_stats()
    partitions = _collect_partitions()

    READ_HISTORY.append(max(0.0, read_speed))
    WRITE_HISTORY.append(max(0.0, write_speed))

    # 2. Render sections
    y = 1
    y = _render_disk_usage(content_win, y, partitions)
    _render_io_activity(content_win, y, read_speed, write_speed)


def render_disk(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """
    Launch the Disk Monitor page loop using the generic `run_page_loop`.

    Args:
        stdscr (curses.window): Main curses window.
        nav_items (list[tuple[str, str, str]]): Navigation items.
        active_page (str): Currently active page identifier.

    Returns:
        int: Key code of quit/navigation key if pressed.
    """

    return run_page_loop(
        stdscr,
        title="Disk & I/O Monitor",
        nav_items=nav_items,
        active_page=active_page,
        render_content_fn=render_disk_page,
        sleep_time=0.3,
    )
