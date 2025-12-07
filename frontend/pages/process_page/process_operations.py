"""
pages/process_page/process_operations.py

Backend operations for process management including kill, pause, resume,
and nice value adjustment.
"""

import os
import signal
import time
from typing import List, Optional

from backend.process import populate_process_list
from backend.process_struct import ProcessInfo
from frontend.pages.process_page.process_page_constants import (
    SORT_KEYS,
    CRITICAL_PROCESSES,
    KILL_RETRY_DELAY,
    SIGTERM,
    SIGKILL,
    SIG_CHECK,
)


def is_critical_process(proc: ProcessInfo) -> bool:
    """Check if a process is critical (dangerous to kill)."""
    if not proc.command:
        return False

    cmd = _extract_command_name(proc.command)

    # Check if it matches any critical process
    for critical in CRITICAL_PROCESSES:
        if cmd.startswith(critical) or cmd == critical:
            return True

    # Also check for PID 1 (init)
    return proc.pid == 1


def _extract_command_name(command: str) -> str:
    """
    Extract base command name from full command string.
    Removes path prefixes, leading dashes (login shells),
    and command arguments to get just the base command name.
    """
    cmd = command.strip()

    # Remove leading dash (for login shells like -bash, -zsh, etc.)
    if cmd.startswith("-"):
        cmd = cmd[1:]

    if "/" in cmd:
        cmd = cmd.split("/")[-1]  # Get just the filename

    cmd = cmd.split()[0]  # Get just the command without args

    return cmd


def get_all_processes(sort_mode: str = "cpu") -> List[ProcessInfo]:
    """Return all processes sorted by the given sort_mode."""
    processes = populate_process_list()
    sort_attr = SORT_KEYS.get(sort_mode, "cpu_percent")
    reverse = sort_attr in ("cpu_percent", "mem_percent")
    processes.sort(key=lambda p: getattr(p, sort_attr, 0), reverse=reverse)
    return processes


def kill_process(pid: int) -> None:
    """
    Attempt to kill a process, trying SIGTERM then SIGKILL.

    Sends SIGTERM for graceful shutdown, waits briefly, then
    sends SIGKILL if process still exists.

    Raises:
        PermissionError: If lacking permissions to kill the process
        ProcessLookupError: If process doesn't exist
    """
    os.kill(pid, SIGTERM)

    time.sleep(KILL_RETRY_DELAY)
    try:
        os.kill(pid, SIG_CHECK)
        os.kill(pid, SIGKILL)
    except (ProcessLookupError, OSError):
        pass


def pause_process(pid: int) -> None:
    """
    Pause (suspend) a process using SIGSTOP.

    Args:
        pid: Process ID to pause

    Raises:
        PermissionError: If lacking permissions to pause the process
        ProcessLookupError: If process doesn't exist
    """
    os.kill(pid, signal.SIGSTOP)


def resume_process(pid: int) -> None:
    """
    Resume a paused process using SIGCONT.

    Args:
        pid: Process ID to resume

    Raises:
        PermissionError: If lacking permissions to resume the process
        ProcessLookupError: If process doesn't exist
    """
    os.kill(pid, signal.SIGCONT)


def set_process_priority(pid: int, nice_value: int) -> None:
    """
    Set the nice value (priority) of a process.

    Args:
        pid: Process ID to adjust
        nice_value: Nice value (-20 to 19, lower = higher priority)

    Raises:
        PermissionError: If lacking permissions to change priority
        ProcessLookupError: If process doesn't exist
        ValueError: If nice_value is out of range
    """
    if not -20 <= nice_value <= 19:
        raise ValueError("Nice value must be between -20 and 19")

    os.setpriority(os.PRIO_PROCESS, pid, nice_value)


def get_process_priority(pid: int) -> int:
    """
    Get the current nice value of a process.

    Args:
        pid: Process ID to query

    Returns:
        Current nice value of the process

    Raises:
        ProcessLookupError: If process doesn't exist
    """
    return os.getpriority(os.PRIO_PROCESS, pid)


def get_process_status(proc: ProcessInfo) -> str:
    """
    Get a human-readable status string for a process.

    Args:
        proc: ProcessInfo object

    Returns:
        Status string (e.g., "Running", "Sleeping", "Stopped", "Zombie")
    """
    stat = proc.stat or ""

    if not stat:
        return "Unknown"

    # First character indicates process state
    state_char = stat[0].upper()

    state_map = {
        "R": "Running",
        "S": "Sleeping",
        "D": "Disk Sleep",
        "T": "Stopped",
        "Z": "Zombie",
        "X": "Dead",
        "I": "Idle",
    }

    return state_map.get(state_char, "Unknown")


def is_process_stopped(proc: ProcessInfo) -> bool:
    """
    Check if a process is currently stopped/suspended.

    Args:
        proc: ProcessInfo object

    Returns:
        True if process is stopped, False otherwise
    """
    stat = proc.stat or ""
    return stat.startswith("T") if stat else False


def is_zombie_process(proc: ProcessInfo) -> bool:
    """
    Check if a process is a zombie (already terminated).

    Zombie processes cannot be killed, paused, resumed, or reniced
    because they are already dead and just waiting to be reaped.

    Parameters:
        proc: ProcessInfo object

    Returns:
        True if process is zombie, False otherwise
    """
    stat = proc.stat or ""
    return stat.startswith("Z") if stat else False


def can_modify_process(pid: int, current_user_pid: int) -> tuple[bool, Optional[str]]:
    """
    Check if the current process can modify the target process.

    Args:
        pid: Target process ID
        current_user_pid: Current process ID

    Returns:
        Tuple of (can_modify, reason_if_not)
    """
    # Can't modify ourselves
    if pid in (current_user_pid, os.getpid()):
        return False, "Cannot modify own process"

    # Can't modify PID 1
    if pid == 1:
        return False, "Cannot modify init process"

    # Check if we have permission (will need to actually try the operation)
    return True, None


def get_process_by_pid(processes: List[ProcessInfo], pid: int) -> Optional[ProcessInfo]:
    """
    Find a process in the list by PID.

    Args:
        processes: List of ProcessInfo objects
        pid: Process ID to find

    Returns:
        ProcessInfo object if found, None otherwise
    """
    for proc in processes:
        if proc.pid == pid:
            return proc
    return None


def get_process_display_name(proc: ProcessInfo) -> str:
    """
    Get a clean display name for a process.

    Args:
        proc: ProcessInfo object

    Returns:
        Clean process name suitable for display
    """
    cmd = proc.command or "unknown"
    if "/" in cmd:
        cmd = cmd.split("/")[-1]
    return cmd.split()[0] if cmd else "unknown"
