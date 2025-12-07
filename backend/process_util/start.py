"""
start.py

Provides functions to retrieve and format process start times (ps-style START column)
for Linux processes using /proc/[pid]/stat and /proc/uptime.

Shows:
- Converting process start ticks to epoch seconds
- Formatting start time into HH:MM, MonDD, or YYYY depending on age
- Handling invalid fields, missing files, and read errors gracefully

Dependencies:
- Standard Python libraries: os, time
- backend.file_helpers for safe file reading
- backend.process_constants for field indices
- backend.process_util.stat for reading process stat fields
"""

import os
import time
from backend.process_constants import ProcessStateIndex, UptimeIndex
from backend.process_util.stat import read_process_stat_fields
from backend.file_helpers import read_file


def _interpret_process_start(fields: list[str], _pid: int) -> str:
    """
    Helper:
    Converts /proc/[pid]/stat fields into a ps-style START column string.

    Args:
        fields (list[str]): List of fields from /proc/[pid]/stat.
        _pid (int): Process ID (used for error reporting).

    Returns:
        str: Formatted START column string or an error message if calculation fails.
    """

    try:
        start_time_seconds = read_process_start_epoch(fields)
        return _format_start_column(start_time_seconds)
    except (ValueError, IndexError) as e:
        return f"Error: {e}"


def read_process_start_epoch(fields: list[str]) -> float:
    """
    Calculates process start time in epoch seconds.

    Args:
        fields (list[str]): List of fields from /proc/[pid]/stat.

    Returns:
        float: Process start time in epoch seconds.

    Raises:
        ValueError: If stat fields are invalid or STARTTIME is missing.
        RuntimeError: If /proc/uptime cannot be read.
    """

    uptime_path = "/proc/uptime"

    if not fields or len(fields) <= ProcessStateIndex.STARTTIME:
        raise ValueError("Invalid stat fields, cannot read STARTTIME")

    start_ticks = int(fields[ProcessStateIndex.STARTTIME])
    clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])

    uptime_content = read_file(uptime_path)
    if not uptime_content:
        raise RuntimeError("Unable to read {uptime_path}")

    uptime_fields = uptime_content.split()
    uptime_seconds = float(uptime_fields[UptimeIndex.SYSTEM_UPTIME])

    now_seconds = time.time()
    start_time_seconds = now_seconds - (uptime_seconds - start_ticks / clock_ticks)
    return start_time_seconds


def _format_start_column(start_time_seconds: float) -> str:
    """
    Helper:
    Formats epoch seconds into a ps aux-style START column string.

    Args:
        start_time_seconds (float): Process start time in epoch seconds.

    Returns:
        str: Formatted start time as HH:MM, MonDD, or YYYY depending on age.
    """

    start_tm = time.localtime(start_time_seconds)
    now_tm = time.localtime(time.time())

    if start_tm.tm_year == now_tm.tm_year and start_tm.tm_yday == now_tm.tm_yday:
        return time.strftime("%H:%M", start_tm)
    if start_tm.tm_year == now_tm.tm_year:
        return time.strftime("%b%d", start_tm)
    return str(start_tm.tm_year)


def get_process_start(pid: int) -> str:
    """
    Retrieves the ps-style START column for a process.

    Args:
        pid (int): Process ID.

    Returns:
        str: Formatted start time for the process, or an error message.
    """

    fields = read_process_stat_fields(pid)
    return _interpret_process_start(fields, pid)
