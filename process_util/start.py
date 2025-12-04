"""
start.py

Retrieve and format process start time (ps-style START column) for Linux processes.
Refactored to use file_helpers.read_file for file reading.
"""

import os
import time
from process_constants import ProcessStateIndex, UptimeIndex
from process_util.stat import read_process_stat_fields
from file_helpers import read_file


def _interpret_process_start(fields: list[str], _pid: int) -> str:
    """
    Converts the starttime field from /proc/[pid]/stat into ps-style START column.
    """
    try:
        start_time_seconds = read_process_start_epoch(fields)
        return _format_start_column(start_time_seconds)
    except (ValueError, IndexError) as e:
        return f"Error: {e}"


def read_process_start_epoch(fields: list[str]) -> float:
    """
    Calculates the process start time in epoch seconds using /proc/uptime.
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
    Formats epoch seconds into a ps aux START column string.
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
    Return the process start time formatted like 'START' column in ps aux.
    """
    fields = read_process_stat_fields(pid)
    return _interpret_process_start(fields, pid)
