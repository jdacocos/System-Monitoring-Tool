"""
memory_info.py

Provides functions to retrieve and calculate system memory stats from the
Linux kernel.

Features:
- Virtual memory usage (total, used, free, available, etc.)
- Swap memory usage (total, used, free, I/O)
"""

from collections import namedtuple
from backend.file_helpers import read_file

Vmem = namedtuple(
    "Vmem",
    [
        "total",
        "available",
        "percent",
        "used",
        "free",
        "active",
        "inactive",
        "buffers",
        "cached",
        "shared",
        "slab",
    ],
)

Smem = namedtuple("Smem", ["total", "used", "free", "percent", "sin", "sout"])


def parse_meminfo() -> dict:
    """
    Reads memory statistics from /proc/meminfo.

    Returns:
        dict: Mapping of memory labels to byte values.
    """
    data = read_file("/proc/meminfo")
    if data is None:
        return {}

    info = {}

    for line in data.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        parts = value.split()

        if not parts:
            continue

        # convert kB → bytes
        info[key] = int(parts[0]) * 1024

    return info


def get_virtual_memory() -> Vmem:
    """
    Retrieves system virtual memory usage statistics.

    Returns:
        Vmem: Named tuple containing virtual memory fields.
    """
    mem = parse_meminfo()

    total = mem.get("MemTotal", 0)
    free = mem.get("MemFree", 0)
    buffers = mem.get("Buffers", 0)
    cached = mem.get("Cached", 0)
    sreclaimable = mem.get("SReclaimable", 0)
    shmem = mem.get("Shmem", 0)
    active = mem.get("Active", 0)
    inactive = mem.get("Inactive", 0)
    slab = mem.get("Slab", 0)

    available = mem.get("MemAvailable", free + buffers + cached + sreclaimable)
    used = total - available
    percent = (used / total * 100) if total else 0

    return Vmem(
        total,
        available,
        percent,
        used,
        free,
        active,
        inactive,
        buffers,
        cached,
        shmem,
        slab,
    )


def get_swap_memory() -> Smem:
    """
    Retrieves swap memory usage and I/O statistics.

    Returns:
        Smem: Named tuple containing swap memory fields.
    """
    mem = parse_meminfo()

    total = mem.get("SwapTotal", 0)
    free = mem.get("SwapFree", 0)
    used = total - free
    percent = (used / total * 100) if total else 0

    sin = 0
    sout = 0

    vmstat_data = read_file("/proc/vmstat")
    if vmstat_data is not None:
        for line in vmstat_data.splitlines():
            if line.startswith("pswpin"):
                sin = int(line.split()[1]) * 4096  # pages → bytes
            elif line.startswith("pswpout"):
                sout = int(line.split()[1]) * 4096  # pages → bytes

    return Smem(total, used, free, percent, sin, sout)
