"""
time.py

This module provides functions to retrieve and format the total CPU time of a process
in a style consistent with the 'TIME' column of the `ps aux` command.

Functions:
    _format_time_column(total_seconds: float) -> str
        Helper function to convert total CPU time in seconds into a ps-style TIME string.
        Formats:
            - M:SS          for durations less than 1 hour
            - H:MM:SS       for durations of 1 hour or more
            - D-HH:MM:SS    for durations of 1 day or more

    get_process_time(pid: int) -> str
        Returns the total CPU time consumed by a process formatted as '[[dd-]hh:]mm:ss'.
        Handles unreadable or non-existent processes gracefully by returning '0:00'.

Notes:
    - The TIME column represents cumulative CPU usage, not wall-clock time.
    - Uses /proc/<pid>/stat to retrieve user and system CPU jiffies for the process.
    - Converts jiffies to seconds using system clock ticks (SC_CLK_TCK).
"""

import os
import time
from process_util.cpu_percent import _read_proc_pid_time
from process_constants import TimeFormatIndex


def _format_time_column(total_seconds: float) -> str:
    """
    Helper:
    Convert total CPU time in seconds into ps aux TIME format:
        - M:SS for <1 hour
        - H:MM:SS for >=1 hour
        - D-HH:MM:SS for >=1 day
    """
    total_seconds = int(total_seconds)

    days = total_seconds // TimeFormatIndex.SECONDS_PER_DAY
    remainder = total_seconds % TimeFormatIndex.SECONDS_PER_DAY

    hours = remainder // TimeFormatIndex.SECONDS_PER_HOUR
    remainder %= TimeFormatIndex.SECONDS_PER_HOUR

    minutes = remainder // TimeFormatIndex.SECONDS_PER_MINUTE
    seconds = remainder % TimeFormatIndex.SECONDS_PER_MINUTE

    if days > 0:
        return f"{days}-{hours:02}:{minutes:02}:{seconds:02}"
    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"  # M:SS


def get_process_time(pid: int) -> str:
    """
    Returns the total CPU time of a process formatted like the TIME column in ps aux.

    Parameters:
        pid (int): Process ID

    Returns:
        str: CPU time as '[[dd-]hh:]mm:ss', or default '0:00' if unreadable
    """
    total_jiffies = _read_proc_pid_time(pid)
    if total_jiffies <= 0:
        return TimeFormatIndex.DEFAULT_TIME

    total_seconds = total_jiffies / os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    return _format_time_column(total_seconds)
