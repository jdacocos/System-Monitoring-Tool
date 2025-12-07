"""
cpu_info.py

Provides functions to retrieve CPU information on Linux systems.

Shows:
- Logical and physical CPU counts
- Current CPU frequency
- Per-core CPU usage percentages over a time interval
- Composite CPU statistics including overall usage

Integrates with backend file helpers to:
- Parse /proc/cpuinfo for core counts and frequency
- Parse /proc/stat for CPU time values
- Calculate CPU usage percentages in a structured format
"""

import os
import time
from collections import namedtuple
from backend.file_helpers import read_file

CpuFreq = namedtuple("CpuFreq", ["current", "min", "max"])


# ==================== CPU Counts ==================== #


def get_logical_cpu_count() -> int:
    """
    Returns the number of logical CPUs in the system.

    Returns:
        int: Number of logical CPU cores detected via os.cpu_count().
    """
    
    return os.cpu_count()


def get_physical_cpu_count() -> int | None:
    """
    Determines the number of physical CPU cores by counting
    unique (physical id, core id) pairs from /proc/cpuinfo.

    Returns:
        int | None: Number of physical CPU cores, or None if unavailable.
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
        CpuFreq | None: Named tuple with fields:
            current (float): Current CPU frequency in MHz.
            min (float): Minimum CPU frequency (0.0 if unavailable).
            max (float): Maximum CPU frequency (0.0 if unavailable).
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
    Reads /proc/stat and returns lines related to CPU usage.

    Returns:
        list[str]: Lines beginning with 'cpu' from /proc/stat.
    """

    data = read_file("/proc/stat")
    if data is None:
        return []

    return [line for line in data.splitlines() if line.startswith("cpu")]


def parse_cpu_line(line: str) -> list[int]:
    """
    Parses a single CPU usage line from /proc/stat.

    Args:
        line (str): A line starting with 'cpuX'.

    Returns:
        list[int]: List of CPU time values as integers.
    """

    parts = line.split()
    return list(map(int, parts[1:]))


def cpu_totals() -> list[tuple[int, int]]:
    """
    Computes total and idle CPU time for each physical/logical core.

    Returns:
        list[tuple[int, int]]: List of tuples (total_time, idle_time) per core.
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
    Calculates per-core CPU usage percentages over a specified interval.

    Args:
        interval (float): Time in seconds to sample CPU statistics.

    Returns:
        list[float]: CPU usage percentages for each core, rounded to 1 decimal place.
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
    Returns a composite dictionary of CPU statistics.

    Returns:
        dict: {
            "overall" (float): Average CPU usage across all cores.
            "per_core" (list[float]): Usage percentages per core.
            "freq" (CpuFreq | None): CPU frequency information.
            "logical" (int): Number of logical CPU cores.
            "physical" (int | None): Number of physical CPU cores.
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
