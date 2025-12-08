"""
cpu_percent.py

Provides functions for calculating CPU usage percentages for processes
and the system on Linux.

Shows:
- Total system CPU jiffies reading from /proc/stat
- Per-process CPU jiffies reading from /proc/<pid>/stat
- CPU usage percentage calculation using cached previous readings
- Cache management to support repeated calls without blocking

Integrates with backend file helpers and process constants to:
- Compute process CPU usage relative to total system CPU
- Handle missing or inaccessible processes gracefully
- Avoid recalculating CPU usage from scratch for each call
"""

import os
from backend.process_constants import CpuStatIndex, ProcessStateIndex
from backend.file_helpers import read_lines, read_file

# caches for previous readings
_LAST_TOTAL_JIFFIES: dict[int, int] = {}
_LAST_PROC_JIFFIES: dict[int, int] = {}


def _read_proc_stat_total() -> int:
    """
    Helper:
    Returns the total system CPU jiffies from /proc/stat.

    Returns:
        int: Sum of USER, NICE, SYSTEM, and IDLE jiffies.
             Returns 0 if /proc/stat cannot be read or is malformed.
    """
    total_jiffies = 0
    stat_path = "/proc/stat"
    lines = read_lines(stat_path)

    if lines:
        first_line = lines[0]
        if first_line.startswith("cpu "):
            fields = first_line.split()
            try:
                total_jiffies = (
                    int(fields[CpuStatIndex.USER + 1])
                    + int(fields[CpuStatIndex.NICE + 1])
                    + int(fields[CpuStatIndex.SYSTEM + 1])
                    + int(fields[CpuStatIndex.IDLE + 1])
                )
            except (IndexError, ValueError):
                total_jiffies = 0

    return total_jiffies


def read_proc_pid_time(pid: int) -> int:
    """
    Returns the total CPU jiffies (utime + stime) used by a specific process.

    Args:
        pid (int): Process ID.

    Returns:
        int: Sum of utime and stime jiffies for the process.
             Returns 0 if the process does not exist or cannot be read.
    """
    stat_path = f"/proc/{pid}/stat"
    total_proc_jiffies = 0
    content: str | None = read_file(stat_path)

    if content is not None:
        fields = content.split()
        try:
            if len(fields) > ProcessStateIndex.STIME:
                utime = int(fields[ProcessStateIndex.UTIME])
                stime = int(fields[ProcessStateIndex.STIME])
                total_proc_jiffies = utime + stime
        except (IndexError, ValueError):
            total_proc_jiffies = 0

    return total_proc_jiffies


def get_process_cpu_percent(pid: int) -> float:
    """
    Returns the CPU usage percentage of a process using cached previous readings.

    Args:
        pid (int): Process ID.

    Returns:
        float: CPU usage percentage for the process.
               Returns CpuStatIndex.CPU_PERCENT_INVALID if previous readings
               are missing, the process does not exist, or delta is too small.
    """

    cpu_percent = CpuStatIndex.CPU_PERCENT_INVALID

    proc_jiffies_current = read_proc_pid_time(pid)
    total_jiffies_current = _read_proc_stat_total()

    if pid in _LAST_PROC_JIFFIES and pid in _LAST_TOTAL_JIFFIES:
        delta_proc = proc_jiffies_current - _LAST_PROC_JIFFIES[pid]
        delta_total = total_jiffies_current - _LAST_TOTAL_JIFFIES[pid]

        if delta_total > CpuStatIndex.MIN_DELTA_TOTAL:
            core_count = os.cpu_count() or CpuStatIndex.CPU_DEFAULT_COUNT
            cpu_percent = (
                (delta_proc / delta_total) * CpuStatIndex.CPU_PERCENT_SCALE / core_count
            )
            cpu_percent = min(
                max(cpu_percent, CpuStatIndex.CPU_PERCENT_INVALID),
                CpuStatIndex.CPU_PERCENT_SCALE,
            )
            cpu_percent = round(cpu_percent, CpuStatIndex.CPU_PERCENT_ROUND_DIGITS)

    # update caches **after calculating or deciding on invalid**
    _LAST_PROC_JIFFIES[pid] = proc_jiffies_current
    _LAST_TOTAL_JIFFIES[pid] = total_jiffies_current

    return cpu_percent


def reset_cpu_cache() -> None:
    """
    Clear the internal CPU jiffy caches.

    Returns:
        None
    """
    _LAST_PROC_JIFFIES.clear()
    _LAST_TOTAL_JIFFIES.clear()
