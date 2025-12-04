"""
time.py

This module provides functions to retrieve and format the total CPU time of a process
in a style consistent with the 'TIME' column of the `ps aux` command.

Functions:
    format_time_column(total_seconds: float) -> str
        Convert total CPU time in seconds into a ps-style TIME string.
    get_process_time(pid: int) -> str
        Returns the total CPU time consumed by a process formatted as '[[dd-]hh:]mm:ss'.
"""

import os
from backend.process_constants import TimeFormatIndex
from backend.process_util.cpu_percent import read_proc_pid_time


def format_time_column(total_seconds: float) -> str:
    """
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
    total_jiffies = read_proc_pid_time(pid)
    if total_jiffies <= 0:
        return TimeFormatIndex.DEFAULT_TIME

    total_seconds = total_jiffies / os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    return format_time_column(total_seconds)
