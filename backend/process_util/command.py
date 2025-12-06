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

from backend.process_util.stat import read_process_stat_fields, base_state
from backend.file_helpers import read_file


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
    Returns the command line of a process (COMMAND column in ps aux).
    Fallback order:
      1. /proc/<pid>/cmdline
      2. /proc/<pid>/comm for kernel threads
      3. [zombie] for zombie processes
      4. [unknown] if all else fails
    """
    result = "[unknown]"
    try:
        # 1. Try full command line first
        cmd = _read_cmdline(pid)
        if cmd:
            result = cmd
        else:
            # 2. Read process stat for state
            fields = read_process_stat_fields(pid)
            state = base_state(fields) if fields else "?"

            # 3. Handle zombie processes
            if state == "Z":
                result = "[zombie]"
            # 4. Handle kernel threads and other special states
            elif state in {"I", "K", "R", "S", "D", "T", "t", "X", "x", "W"}:
                comm_name = _read_comm(pid)
                result = (
                    f"[{comm_name}]" if comm_name != "unknown" else f"[kernel {pid}]"
                )
            # 5. Else keep default "[unknown]"

    except FileNotFoundError:
        result = "[PID not found]"
    except PermissionError:
        result = "[Permission denied]"
    except OSError:
        result = "[error]"

    return result
