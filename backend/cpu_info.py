"""
cpu_info.py

Provides functions to retrieve CPU information on Linux systems.

Features:
- Logical CPU count
- Physical CPU count
- Current CPU frequency
- Per-core CPU usage and percentage over a time interval

All data is retrieved using system calls or by parsing kernel files.
"""

import os
import time
from collections import namedtuple
from backend.file_helpers import read_file

CpuFreq = namedtuple("CpuFreq", ["current", "min", "max"])


# ==================== CPU Counts ==================== #


def get_logical_cpu_count() -> int:
    """
    Returns the number of logical CPUs in the system
    using os.cpu_count().
    """
    return os.cpu_count()


def get_physical_cpu_count() -> int | None:
    """
    Determines the number of physical CPU cores by counting
    unique (physical id, core id) pairs from /proc/cpuinfo.

    physical id -> CPU socket
    core id     -> Core within the socket

    Returns:
        int | None: Count of physical cores, or None if unavailable.
    """
    cpuinfo = read_file("/proc/cpuinfo")
    if cpuinfo is None:
        return None

    phys_core_pairs = set()
    phys_id = None
    core_id = None

    for line in cpuinfo.splitlines():
        if line.startswith("physical id"):
            phys_id = int(line.split(":")[1].strip())
        elif line.startswith("core id"):
            core_id = int(line.split(":")[1].strip())

            if phys_id is not None and core_id is not None:
                phys_core_pairs.add((phys_id, core_id))

            phys_id = None
            core_id = None

    return len(phys_core_pairs) if phys_core_pairs else None


# ==================== CPU Frequency ==================== #


def get_cpu_freq() -> CpuFreq | None:
    """
    Reads the current CPU frequency (MHz) from /proc/cpuinfo.

    Returns:
        CpuFreq | None: Named tuple with current, min, and max frequency.
    """
    cpuinfo = read_file("/proc/cpuinfo")
    if cpuinfo is None:
        return None

    current_freq = None
    for line in cpuinfo.split("\n"):
        if "cpu MHz" in line:
            try:
                current_freq = float(line.split(":")[1].strip())
            except ValueError:
                current_freq = None
            break

    if current_freq is None:
        return None

    return CpuFreq(current=current_freq, min=0.0, max=0.0)


# ==================== CPU Percent Per Core ==================== #


def read_proc_stat() -> list[str]:
    """
    Reads /proc/stat and returns CPU usage lines.

    Returns:
        list[str]: Lines beginning with 'cpu'.
    """
    data = read_file("/proc/stat")
    if data is None:
        return []

    return [line for line in data.splitlines() if line.startswith("cpu")]


def parse_cpu_line(line: str) -> list[int]:
    """
    Parses a single CPU usage line from /proc/stat.

    Args:
        line (str): Line starting with 'cpuX'.

    Returns:
        list[int]: CPU time values.
    """
    parts = line.split()
    return list(map(int, parts[1:]))


def cpu_totals() -> list[tuple[int, int]]:
    """
    Computes total time and idle time for each CPU core.

    Returns:
        list[tuple[int, int]]: (total_time, idle_time) per core.
    """
    lines = read_proc_stat()

    core_lines = [
        line for line in lines if line.startswith("cpu") and not line.startswith("cpu ")
    ]

    totals = []
    for line in core_lines:
        values = parse_cpu_line(line)
        idle_time = values[3] + values[4]
        total_time = sum(values)
        totals.append((total_time, idle_time))

    return totals


def get_cpu_percent_per_core(interval: float = 0.1) -> list[float]:
    """
    Calculates per-core CPU usage over a time interval.

    Args:
        interval (float): Time to sample CPU statistics.

    Returns:
        list[float]: CPU usage percentages for each core.
    """
    before = cpu_totals()
    time.sleep(interval)
    after = cpu_totals()

    percentages = []

    for (total_before, idle_before), (total_after, idle_after) in zip(before, after):
        total_delta = total_after - total_before
        idle_delta = idle_after - idle_before

        if total_delta <= 0:
            percentages.append(0.0)
        else:
            usage = 100.0 * (1 - idle_delta / total_delta)
            percentages.append(round(usage, 1))

    return percentages


# ==================== Composite Test Function ==================== #


def get_cpu_stats() -> dict:
    """
    Returns a composite CPU statistics dictionary.

    Returns:
        dict: {
            "overall": float,
            "per_core": list[float],
            "freq": CpuFreq | None,
            "logical": int,
            "physical": int | None
        }
    """
    per_core = get_cpu_percent_per_core(interval=0.1)
    overall = sum(per_core) / len(per_core) if per_core else 0.0

    return {
        "overall": overall,
        "per_core": per_core,
        "freq": get_cpu_freq(),
        "logical": get_logical_cpu_count(),
        "physical": get_physical_cpu_count(),
    }
