"""
nice.py

Provides a function to retrieve the nice value of a process on Linux,
corresponding to the NI column in `ps aux`.

Uses read_process_stat_fields from stat.py and process_constants.py
to safely read /proc files and avoid magic numbers.

Functions:
    get_process_nice(pid: int) -> int:
        Returns the nice value of the given process.
        Handles missing PIDs, permission errors, and kernel threads gracefully.
"""

from backend.process_util.stat import read_process_stat_fields
from backend.process_constants import ProcessStateIndex


def get_process_nice(pid: int) -> int:
    """
    Returns the nice value (priority) of a process.

    Fallbacks:
      - Returns the NI value from /proc/<pid>/stat if available.
      - Returns 0 for kernel threads or if data cannot be read.
    """
    nice_val = 0

    try:
        fields = read_process_stat_fields(pid)
        if fields and len(fields) > ProcessStateIndex.NICE:
            nice_val = int(fields[ProcessStateIndex.NICE])
    except (FileNotFoundError, PermissionError, OSError, ValueError, IndexError):
        pass

    return nice_val
