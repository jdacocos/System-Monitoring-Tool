"""
command.py

This module provides a function to retrieve the full command line of a process
on a Linux system, corresponding to the COMMAND column in `ps aux`.

Uses read_file from file_helpers.py to safely read /proc files.

Functions:
    get_process_command(pid: int) -> str:
        Returns the full command line of the given process as a string.
        Handles kernel threads, missing PIDs, and permission errors gracefully.
"""

from process_util.stat import read_process_stat_fields, base_state
from file_helpers import read_file


def _read_cmdline(pid: int) -> str:
    """Read /proc/<pid>/cmdline and return as a space-separated string."""
    cmdline_path = f"/proc/{pid}/cmdline"
    content = read_file(cmdline_path)
    return content.replace("\x00", " ").strip() if content else ""


def _read_comm(pid: int) -> str:
    """Read /proc/<pid>/comm to get the process name (used for kernel threads)."""
    comm_path = f"/proc/{pid}/comm"
    content = read_file(comm_path)
    return content.strip() if content else "unknown"


def get_process_command(pid: int) -> str:
    """
    Returns the command line of a process, corresponding to the COMMAND column in `ps aux`.
    Falls back to comm or stat information for kernel threads or zombie processes.
    """
    try:
        cmd = _read_cmdline(pid)
        if cmd:
            result = cmd
        else:
            fields = read_process_stat_fields(pid)
            state = base_state(fields) if fields else "?"
            if state == "Z":
                result = "[zombie]"
            elif state in {"I", "K", "R", "S", "D", "T", "t", "X", "x", "W"}:
                result = f"[{_read_comm(pid)}]"
            else:
                result = "[unknown]"
    except FileNotFoundError:
        result = "[PID not found]"
    except PermissionError:
        result = "[Permission denied]"
    except OSError:
        result = "[error]"

    return result
