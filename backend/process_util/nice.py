"""
nice.py

This module provides functionality to retrieve the nice value (priority)
of a process on a Linux system, corresponding to the NI column in `ps aux`.

Shows:
- Reading the nice value safely from /proc/<pid>/stat
- Handling missing PIDs, kernel threads, and permission errors
- Returning default values when process data is unavailable

Dependencies:
- backend.process_util.stat for reading process stat fields
- backend.process_constants for field index constants
"""

from backend.process_util.stat import read_process_stat_fields
from backend.process_constants import ProcessStateIndex


def get_process_nice(pid: int) -> int:
    """
    Returns the nice value (priority) of a specific process.

    Args:
        pid (int): Process ID.

    Returns:
        int: Nice value of the process (NI column in ps aux).
             Returns 0 for kernel threads, unreadable processes, or on errors.
    """
    
    nice_val = 0

    try:
        fields = read_process_stat_fields(pid)
        if fields and len(fields) > ProcessStateIndex.NICE:
            nice_val = int(fields[ProcessStateIndex.NICE])
    except (FileNotFoundError, PermissionError, OSError, ValueError, IndexError):
        pass

    return nice_val
