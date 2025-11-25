"""
command.py

This module provides a function to retrieve the full command line of a process
on a Linux system, corresponding to the COMMAND column in `ps aux`.

Functions:
    get_process_command(pid: int) -> str:
        Returns the full command line of the given process as a string.
        Handles kernel threads, missing PIDs, and permission errors gracefully.

Usage Example:
    from process_util.command import get_process_command

    pid = 1234
    command = get_process_command(pid)
    print(f"Process {pid} COMMAND: {command}")
"""

from process_constants import RD_ONLY, UTF_8


def _read_cmdline(pid: int) -> str:
    """Read /proc/<pid>/cmdline and return it as a space-separated string."""
    path = f"/proc/{pid}/cmdline"
    with open(path, RD_ONLY, encoding=UTF_8) as f:
        return f.read().replace("\x00", " ").strip()


def _read_comm(pid: int) -> str:
    """Read /proc/<pid>/comm to get kernel thread name."""
    path = f"/proc/{pid}/comm"
    try:
        with open(path, RD_ONLY, encoding=UTF_8) as f:
            return f.read().strip()
    except OSError:
        return "unknown"


def get_process_command(pid: int) -> str:
    """
    Returns the command line of a process, corresponding to the COMMAND column in `ps aux`.

    Parameters:
        pid (int): Process ID

    Returns:
        str: The full command line if available, or a descriptive placeholder:
            - "[PID not found]" if the process does not exist
            - "[Permission denied]" if /proc/<pid>/cmdline cannot be read
            - "[zombie]" if the process is a zombie
            - "[kthread: <name>]" if the process is a kernel thread (empty cmdline)
    """
    result = "[unknown]"

    try:
        cmd = _read_cmdline(pid)
        if cmd:
            result = cmd
        else:
            result = _classify_empty_cmdline(pid)

    except FileNotFoundError:
        result = "[PID not found]"
    except PermissionError:
        result = "[Permission denied]"
    except OSError:
        result = "[error]"

    return result
