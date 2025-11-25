"""
cpu_percent.py

This module provides functions for calculating CPU usage percentages
for processes and the system on Linux. It reads from the /proc filesystem,
including /proc/stat for total CPU jiffies and /proc/<pid>/stat for process-specific
CPU times (utime + stime).

Functions:
    _read_proc_stat_total(): Helper to sum total system CPU jiffies.
    _read_proc_pid_time(pid): Helper to get total CPU jiffies used by a process.
    get_process_cpu_percent(pid, interval): Calculates CPU usage percentage for a process
        over a specified sampling interval.

All functions rely only on standard libraries: os, time, and typing.

Notes:
    - CPU jiffies are the basic units of CPU time used by the Linux kernel.
    - Percentages are calculated relative to total system CPU time over the interval.
    - Returns CPU_PERCENT_INVALID if calculation cannot be performed (e.g., process
      exits, /proc unavailable, or delta too small).
"""

import os
import time
from typing import Iterator
from process_constants import LNX_FS, RD_ONLY, UTF_8, CpuStatIndex, ProcessStateIndex


def _read_proc_stat_total() -> int:
    """
    Helper: Retrieve total CPU jiffies from /proc/stat.
    Jiffy - basic unit of time Linux kernel uses to measure CPU activity.

    Returns:
        int: Total CPU jiffies (sum of USER, NICE, SYSTEM, IDLE),
             or 0 if /proc/stat cannot be read.
    """
    stat_path = "/proc/stat"
    total_jiffies = 0

    try:
        with open(stat_path, RD_ONLY, encoding=UTF_8) as f:
            first_line = f.readline()
            if first_line.startswith("cpu "):
                # skip the "cpu" label
                cpu_fields = first_line.split()[CpuStatIndex.CPU_LABEL_COLUMN :]

                # Sum USER + NICE + SYSTEM + IDLE (indexes defined in CpuStatIndex)
                total_jiffies = sum(
                    int(cpu_fields[i]) for i in range(CpuStatIndex.IDLE + 1)
                )

    except FileNotFoundError:
        print(f"Error: {stat_path} not found. Cannot read total CPU jiffies.")
    except IndexError:
        print(f"Error: Unexpected format in {stat_path}. Not enough CPU fields.")
    except ValueError:
        print(f"Error: Invalid numeric value found in {stat_path}.")
    return total_jiffies


def _read_proc_pid_time(pid: int) -> int:
    """
    Helper: Retrieve total CPU jiffies used by a process (utime + stime)
    from /proc/<pid>/stat.

    Parameters:
        pid (int): Process ID

    Returns:
        int: Total CPU jiffies for the process, or 0 if process
             does not exist or cannot be read.
    """
    stat_path = f"/proc/{pid}/stat"
    total_proc_jiffies = 0

    try:
        with open(stat_path, RD_ONLY, encoding=UTF_8) as f:
            fields = f.read().split()

            # Ensure required fields exist
            if len(fields) > ProcessStateIndex.STIME:
                utime = int(fields[ProcessStateIndex.UTIME])
                stime = int(fields[ProcessStateIndex.STIME])
                total_proc_jiffies = utime + stime

    except FileNotFoundError:
        print(f"Error: {stat_path} not found. Process may have exited.")
    except IndexError:
        print(f"Error: Unexpected format in {stat_path}. Not enough fields.")
    except ValueError:
        print(f"Error: Invalid numeric value in {stat_path} for utime/stime.")

    return total_proc_jiffies


def get_process_cpu_percent(pid: int, interval: float = 0.1) -> float:
    """
    Calculate the CPU usage percentage of a process over a given interval.

    Parameters:
        pid (int): Process ID
        interval (float): Time interval (seconds) between samples

    Returns:
        float: CPU usage percentage (0.0 - 100.0), or CPU_PERCENT_INVALID if
               the calculation could not be performed.
    """
    # read initial CPU jiffies
    proc_jiffies_start = _read_proc_pid_time(pid)
    total_jiffies_start = _read_proc_stat_total()

    time.sleep(interval)

    # read CPU jiffies after time pass
    proc_jiffies_end = _read_proc_pid_time(pid)
    total_jiffies_end = _read_proc_stat_total()

    delta_proc = proc_jiffies_end - proc_jiffies_start
    delta_total = total_jiffies_end - total_jiffies_start

    # check division by zero
    if delta_total <= CpuStatIndex.MIN_DELTA_TOTAL:
        print(f"Warning: Total jiffies delta too small ({delta_total}).")
        return CpuStatIndex.CPU_PERCENT_INVALID

    cpu_percent = (delta_proc / delta_total) * CpuStatIndex.CPU_PERCENT_SCALE
    return round(cpu_percent, CpuStatIndex.CPU_PERCENT_ROUND_DIGITS)
