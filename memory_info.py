# Get memory usage information

from utilities import read_file
from collections import namedtuple

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
    info = {}
    try:
        data = read_file("/proc/meminfo")
    except Exception:
        return info

    for line in data.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parts = value.split()
        if not parts:
            continue
        # convert from kB to bytes
        info[key] = int(parts[0]) * 1024
    return info


def get_virtual_memory():
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
    mem = parse_meminfo()

    total = mem.get("SwapTotal", 0)
    free = mem.get("SwapFree", 0)
    used = total - free
    percent = (used / total * 100) if total else 0

    # Swap I/O from /proc/vmstat
    sin = 0
    sout = 0
    try:
        vmstat = read_file("/proc/vmstat")
        for line in vmstat.splitlines():
            if line.startswith("pswpin"):
                sin = int(line.split()[1]) * 4096
            elif line.startswith("pswpout"):
                sout = int(line.split()[1]) * 4096
    except Exception:
        pass

    return smem(total, used, free, percent, sin, sout)
