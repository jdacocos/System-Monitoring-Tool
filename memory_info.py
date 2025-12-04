"""
memory_info.py

Provides functions to retrieve and calculate system memory stats from the
Linux kernal.

Features:
- Virtual memory usage (total, used, free, available, etc.)
- Swap memory usage (total, used, free, I/O)
"""

from collections import namedtuple
from utilities import read_file

vmem = namedtuple(
    "vmem",
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
smem = namedtuple("smem", ["total", "used", "free", "percent", "sin", "sout"])


def parse_meminfo():
    """
    Reads memory stats from /proc/meminfo.

    Returns a dictionary where:
    - keys are the memory labels (e.g. 'MemTotal', 'MemFree')
    - values are memory size in bytes
    """

    info = {}

    data = read_file("/proc/meminfo")

    for line in data.splitlines():

        # lines without : are skipped
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        # split value string into list of substrings using whitespace
        parts = value.split()

        # skip line if nothing after colon (no usable data)
        if not parts:
            continue

        # convert from kB to bytes and store in the dictionary under the corresponding key
        info[key] = int(parts[0]) * 1024

    return info


def get_virtual_memory():
    """
    Retrives system memory usage stats.

    Returns a named tuple (vmem) containing:
    - total: total physical memory in bytes
    - available: memory available for allocation in bytes
    - percent: percentage of memory used
    - used: used memory in bytes
    - free: free memory in bytes
    - active: memory actively used in bytes
    - inactive: memory inactive but still allocated in bytes
    - buffers: memory used for buffers in bytes
    - cached: memory used for cache in bytes
    - shmem: shared memory in bytes
    - slab: memory used by kernel slabs in bytes
    """

    mem = parse_meminfo()

    # extract key memory fields, default to 0 if not present
    total = mem.get("MemTotal", 0)
    free = mem.get("MemFree", 0)
    buffers = mem.get("Buffers", 0)
    cached = mem.get("Cached", 0)
    sreclaimable = mem.get("SReclaimable", 0)
    shmem = mem.get("Shmem", 0)
    active = mem.get("Active", 0)
    inactive = mem.get("Inactive", 0)
    slab = mem.get("Slab", 0)

    # calculate derived memory values
    available = mem.get("MemAvailable", free + buffers + cached + sreclaimable)
    used = total - available

    percent = (used / total * 100) if total else 0

    return vmem(
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


def get_swap_memory():
    """
    Retrives swap memory stats from the system.

    Returns a named tuple (smem) containing:
    - total: total swap memory in bytes
    - used: used swap memory in bytes
    - free: free swap memory in bytes
    - percent: percentage of swap used
    - sin: total bytes swapped in from disk
    - sout: total bytes swapped out to disk
    """

    mem = parse_meminfo()

    # extract basic swap memory values
    total = mem.get("SwapTotal", 0)
    free = mem.get("SwapFree", 0)
    used = total - free
    percent = (used / total * 100) if total else 0

    sin = 0
    sout = 0

    # read swap I/O stats from /proc/vmstat
    vmstat = read_file("/proc/vmstat")
    for line in vmstat.splitlines():

        # pages swapped in from disk to RAM
        if line.startswith("pswpin"):
            # convert page count to bytes
            sin = int(line.split()[1]) * 4096

            # pages swapped out from RAM to disk
        elif line.startswith("pswpout"):
            # convert page count to bytes
            sout = int(line.split()[1]) * 4096

    return smem(total, used, free, percent, sin, sout)
