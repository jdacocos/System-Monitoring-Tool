"""
Get CPU information
"""

import time
import os
from collections import namedtuple
from utilities import read_file

cpufreq = namedtuple("cpufreq", ["current", "min", "max"])

# ==================== CPU Counts ==================== #

def get_logical_cpu_count() -> int:
    """
    Counts the number of logical cpu's in the system by calling on the
    cpu_count system call wrapper.
    """
    
    return os.cpu_count()


def get_physical_cpu_count() -> int | None:
    """
    Determines the numer of physical CPU cores by counting unique
    (physical id, core id) pairs.
    Returns the number of unique physical cores.

    physical id -> one CPU socket.
    core id -> one core within that socket.
    """
    
    # set of unique (physical id, core id) pairs
    phys_core_pairs = set()

    phys_id = None
    core_id = None

    cpuinfo = read_file("/proc/cpuinfo")

    for line in cpuinfo.splitlines():
        
        # find "physical id" and store it
        if line.startswith("physical id"):
            phys_id = int(line.split(":")[1])
            
        # find "core id" and store it 
        if line.startswith("core id"):
            core_id = int(line.split(":")[1])

            # add the pair once both values are known
            if phys_id is not None and core_id is not None:
                phys_core_pairs.add((phys_id, core_id))

            # reset for next pair
            phys_id = None
            core_id = None

    return len(phys_core_pairs) if phys_core_pairs else None


# ==================== CPU Frequency ==================== #


def get_cpu_freq() -> cpufreq | None:
    """Returns a dict {current, min, max} or None."""

    cpuinfo = read_file("/proc/cpuinfo")

    if cpuinfo is None:
        return None

    curr = None
    for line in cpuinfo.split("\n"):
        if "cpu MHz" in line:
            try:
                curr = float(line.split(":")[1].strip())
            except:
                curr = None
            break

    if curr is None:
        return None

    return cpufreq(current=curr, min=0.0, max=0.0)


# ==================== CPU Percent Per Core ==================== #


def read_proc_stat() -> list[str]:
    """ 
    Reads /proc/stat.
    Returns only the lines that describe CPU usage.
    """

    data = read_file("/proc/stat")
    return [line for line in data.splitlines() if line.startswith("cpu")]


def parse_cpu_line(line: str) -> list[int]:
    """ 
    Parses a single CPU line from /proc/stat.
    Returns a list of integer CPU time fields for that core.
    """

    parts = line.split()
    
    # skips the label (e.g. cpu0) and converts the remaining fields to integers
    return list(map(int, parts[1:]))


def cpu_totals() -> list[tuple[int, int]]:
    """
    Calculates the total and idle time for each CPU core. 
    Returns a list of (total_time, idle_time) tuples.
    """

    lines = read_proc_stat()

    # keep only per-core CPU lines (cpu0, cpu1, ...)
    core_lines = [l for l in lines if l.startswith("cpu") and not l.startswith("cpu ")]

    totals = []
    for line in core_lines:
        values = parse_cpu_line(line)

        # idle time = idle + iowait fields
        total_idle = values[3] + values[4]

        # calculate total time
        total = sum(values)

        # store result in a tuple
        totals.append((total, total_idle))

    return totals


def get_cpu_percent_per_core(interval: float = 0.1) -> list[float]:
    """
    Calculates per-core CPU usage over a time interval.
    Returns a list of usage percentages for each core.
    """

    # capture CPU usage over the given time window
    before = cpu_totals()
    time.sleep(interval)
    after = cpu_totals()

    percentages = []

    # For each core, pair (total_before, idle_before) with
    # (total_after, idle_after) and compute usage from the deltas
    for (total1, idle1), (total2, idle2) in zip(before, after):
        total_delta = total2 - total1
        idle_delta = idle2 - idle1

        if total_delta <= 0:
            # if counters have not increased, usage cannot be computed
            percentages.append(0.0)
        else:
            # compute CPU usage percentage
            pct = 100.0 * (1 - idle_delta / total_delta)
            percentages.append(round(pct, 1))

    return percentages


# ==================== Test Composite ==================== #


def get_cpu_stats() -> dict:
    """Test Function"""

    per_core = get_cpu_percent_per_core(interval=0.1)
    overall = sum(per_core) / len(per_core) if per_core else 0.0

    return {
        "overall": overall,
        "per_core": per_core,
        "freq": get_cpu_freq(),
        "logical": get_logical_cpu_count(),
        "physical": get_physical_cpu_count(),
    }
