"""
time.py

Provides functions to retrieve and format total CPU time of a process
in a style consistent with the 'TIME' column of the `ps aux` command.

Shows:
- Converting total CPU time in seconds into ps-style TIME string
- Formatting [[dd-]hh:]mm:ss for process CPU usage
- Reading process CPU jiffies and converting to human-readable time

Dependencies:
- Standard Python libraries: os
- backend.process_constants for time constants
- backend.process_util.cpu_percent for process CPU jiffies
"""

import os
from backend.process_constants import TimeFormatIndex
from backend.process_util.cpu_percent import read_proc_pid_time


def format_time_column(total_seconds: float) -> str:
    """
    Convert total CPU time in seconds into ps aux TIME format.

    Format rules:
        - M:SS for durations < 1 hour
        - H:MM:SS for durations >= 1 hour
        - D-HH:MM:SS for durations >= 1 day

    Args:
        total_seconds (float): Total CPU time in seconds.

    Returns:
        str: Formatted TIME string.
    """
    result = ""
    total_seconds = int(total_seconds)
    days = total_seconds // TimeFormatIndex.SECONDS_PER_DAY
    remainder = total_seconds % TimeFormatIndex.SECONDS_PER_DAY
    hours = remainder // TimeFormatIndex.SECONDS_PER_HOUR
    remainder %= TimeFormatIndex.SECONDS_PER_HOUR
    minutes = remainder // TimeFormatIndex.SECONDS_PER_MINUTE
    seconds = remainder % TimeFormatIndex.SECONDS_PER_MINUTE

    if days > 0:
        result = f"{days}-{hours:02}:{minutes:02}:{seconds:02}"
    elif hours > 0:
        result = f"{hours}:{minutes:02}:{seconds:02}"
    else:
        result = f"{minutes}:{seconds:02}"  # M:SS

    return result


def get_process_time(pid: int) -> str:
    """
    Retrieve the total CPU time of a process formatted like the TIME column in ps aux.

    Args:
        pid (int): Process ID.

    Returns:
        str: CPU time formatted as '[[dd-]hh:]mm:ss'.
             Returns '0:00' if the process cannot be read or has no CPU time.
    """
    result = TimeFormatIndex.DEFAULT_TIME
    total_jiffies = read_proc_pid_time(pid)

    if total_jiffies > 0:
        total_seconds = total_jiffies / os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        result = format_time_column(total_seconds)

    return result
