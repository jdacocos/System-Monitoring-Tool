"""
start.py

This module provides functions to retrieve and format the start time of
a process on a Linux system, in a style consistent with the 'START' column
of the `ps aux` command.

Functions included:

- get_process_start(pid: int) -> str
    Retrieves the process start time for a given PID and formats it as:
        - 'HH:MM' if the process started today
        - 'MonDD' if the process started this year but not today
        - 'YYYY' if the process started in a previous year

Helper functions (internal use only):

- _interpret_process_start(fields: list[str], pid: int) -> str
    Converts the /proc/[pid]/stat fields into a formatted START string.

- _read_process_start_epoch(fields: list[str]) -> float
    Computes the process start time in epoch seconds based on /proc/[pid]/stat
    and /proc/uptime.

- _format_start_column(start_time_seconds: float) -> str
    Formats epoch seconds into a string suitable for the ps-style START column.

All functions handle errors gracefully, returning informative messages if the
process no longer exists or fields are invalid.

Dependencies:
    - os
    - time
    - process_util.stat for reading process stat fields
"""

import os
import time
from process_constants import RD_ONLY, UTF_8, ProcessStateIndex, UptimeIndex
from process_util.stat import _read_process_stat_fields


def _interpret_process_start(fields: list[str], _pid: int) -> str:
    """
    Helper:
    Converts the starttime field from /proc/[pid]/stat into ps-style START column string.

    Parameters:
        fields (list[str]): Fields from /proc/[pid]/stat
        pid (int): Process ID

    Returns:
        str: START column string ('HH:MM', 'MonDD', 'YYYY') or error message
    """
    try:
        start_time_seconds = _read_process_start_epoch(fields)
        return _format_start_column(start_time_seconds)
    except (ValueError, IndexError) as e:
        return f"Error: {e}"


def _read_process_start_epoch(fields: list[str]) -> float:
    """
    Helper:
    Calculates the process start time in epoch seconds.

    Parameters:
        fields (list[str]): Fields from /proc/[pid]/stat

    Returns:
        float: Epoch seconds of process start time
    """
    uptime_path = "/proc/uptime"

    if not fields or len(fields) <= ProcessStateIndex.STARTTIME:
        raise ValueError("Invalid stat fields, cannot read STARTTIME")

    start_ticks = int(fields[ProcessStateIndex.STARTTIME])
    clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])

    with open(uptime_path, RD_ONLY, encoding=UTF_8) as f:
        uptime_fields = f.read().split()
        uptime_seconds = float(uptime_fields[UptimeIndex.SYSTEM_UPTIME])

    now_seconds = time.time()
    start_time_seconds = now_seconds - (uptime_seconds - start_ticks / clock_ticks)
    return start_time_seconds


def _format_start_column(start_time_seconds: float) -> str:
    """
    Formats epoch seconds into a ps aux START column string.

    Parameters:
        start_time_seconds (float): Epoch seconds of process start time

    Returns:
        str: START column string ('HH:MM', 'MonDD', 'YYYY')
    """
    start_tm = time.localtime(start_time_seconds)
    now_tm = time.localtime(time.time())

    if (start_tm.tm_year == now_tm.tm_year) and (start_tm.tm_yday == now_tm.tm_yday):
        # Started today - HH:MM
        return time.strftime("%H:%M", start_tm)

    if start_tm.tm_year == now_tm.tm_year:
        # Started this year - MonDD
        return time.strftime("%b%d", start_tm)

    # Started previous year - YYYY
    return str(start_tm.tm_year)


def get_process_start(pid: int) -> str:
    """
    Returns the process start time formatted like the 'START' column in ps aux.

    Parameters:
        pid (int): Process ID

    Returns:
        str: Start time as 'HH:MM', 'MonDD', or 'YYYY', or error message if unavailable
    """
    fields = _read_process_stat_fields(pid)
    return _interpret_process_start(fields, pid)
