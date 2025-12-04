"""
mem_percent.py

This module provides functions for calculating memory usage
of processes on a Linux system, including:

- get_process_mem_percent(pid): returns the memory usage
  of a specific process as a percentage of total system memory.

It uses information from:

- /proc/<pid>/statm via get_process_rss
- /proc/meminfo via _read_meminfo_total

Memory usage percentages are returned as floats between 0.0 and 100.0.

Dependencies:
    - Standard Python libraries: os
    - process_util.rss for RSS and total memory readings
"""

from process_constants import MemInfoIndex
from process_util.rss import get_process_rss, read_meminfo_total


def get_process_mem_percent(pid: int) -> float:
    """
    Calculate the memory usage percentage of a process.

    Parameters:
        pid (int): Process ID

    Returns:
        float: Memory usage percent (0.0 - 100.0)
    """
    rss_kb = get_process_rss(pid)
    total_mem_kb = read_meminfo_total()

    # check division by zero or invalid total memory
    if total_mem_kb <= MemInfoIndex.MEM_INVALID:
        print(f"Warning: Total system memory invalid or unreadable for PID {pid}.")
        return float(MemInfoIndex.MEM_INVALID)

    mem_percent = (rss_kb / total_mem_kb) * MemInfoIndex.MEM_PERCENT_SCALE
    return round(mem_percent, MemInfoIndex.MEM_PERCENT_ROUND_DIGITS)
