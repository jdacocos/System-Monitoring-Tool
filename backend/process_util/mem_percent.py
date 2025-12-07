"""
mem_percent.py

Provides functions for calculating memory usage percentages of processes
on Linux systems.

Shows:
- Per-process memory usage as a percentage of total system memory
- Safe handling of unreadable /proc/<pid>/statm or /proc/meminfo
- Rounded float values between 0.0 and 100.0

Integrates with backend process_util functions:
- get_process_rss() to read resident set size (RSS) of a process
- read_meminfo_total() to read total system memory from /proc/meminfo
"""

from backend.process_constants import MemInfoIndex
from backend.process_util.rss import get_process_rss, read_meminfo_total


def get_process_mem_percent(pid: int) -> float:
    """
    Calculates the memory usage percentage of a specific process.

    Args:
        pid (int): Process ID.

    Returns:
        float: Memory usage percentage of the process (0.0 - 100.0).
               Returns MemInfoIndex.MEM_INVALID if total system memory
               is unreadable or zero.
    """

    rss_kb = get_process_rss(pid)
    total_mem_kb = read_meminfo_total()

    # check division by zero or invalid total memory
    if total_mem_kb <= MemInfoIndex.MEM_INVALID:
        print(f"Warning: Total system memory invalid or unreadable for PID {pid}.")
        return float(MemInfoIndex.MEM_INVALID)

    mem_percent = (rss_kb / total_mem_kb) * MemInfoIndex.MEM_PERCENT_SCALE
    return round(mem_percent, MemInfoIndex.MEM_PERCENT_ROUND_DIGITS)
