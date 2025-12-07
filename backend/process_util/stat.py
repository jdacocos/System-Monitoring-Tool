"""
stat.py

Provides functions for retrieving and interpreting process state information
from Linux /proc/<pid>/stat files. Converts raw kernel states and flags into
human-readable strings, similar to the STAT column in the `ps` command.

Shows:
- Reading and splitting /proc/<pid>/stat fields
- Extracting base process state (R, S, D, etc.)
- Detecting session leader processes
- Flagging high/low priority processes
- Identifying multi-threaded and locked memory processes
- Detecting foreground processes

Dependencies:
- Standard Python libraries: os
- backend.file_helpers for safe file reading
- backend.process_constants for field indices and stat maps
- backend.process_util.tty for terminal lookups
"""

import os
from backend.process_constants import ProcessStateIndex, StatMapIndex
from backend.process_util.tty import read_tty_nr_to_name
from backend.file_helpers import read_file

# Simple PID -> stat cache
_STAT_CACHE: dict[int, str] = {}


def read_process_stat_fields(pid: int) -> list[str]:
    """
    Reads /proc/<pid>/stat and splits the content into fields.

    Args:
        pid (int): Process ID.

    Returns:
        list[str]: List of stat fields. Returns empty list if the file cannot be read.
    """

    stat_path = f"/proc/{pid}/stat"
    content = read_file(stat_path)
    if not content:
        print(f"[WARN] Could not read {stat_path}")
        return []
    return content.split()


def base_state(fields: list[str]) -> str:
    """
    Extracts the base process state character.

    Args:
        fields (list[str]): Fields from /proc/<pid>/stat.

    Returns:
        str: Base process state character (e.g., R, S, D). Returns default if unavailable.
    """

    try:
        return StatMapIndex.STATE_MAP.get(
            fields[ProcessStateIndex.STATE], StatMapIndex.DEFAULT_STAT
        )
    except IndexError:
        return StatMapIndex.DEFAULT_STAT


def _session_leader_flag(fields: list[str], pid: int) -> str:
    """
    Helper:
    Returns 's' if the process is a session leader.

    Args:
        fields (list[str]): Fields from /proc/<pid>/stat.
        pid (int): Process ID.

    Returns:
        str: 's' if session leader, otherwise empty string.
    """

    try:
        return (
            StatMapIndex.FLAG_MAP["session_leader"]
            if int(fields[ProcessStateIndex.SESSION]) == pid
            else ""
        )
    except (ValueError, IndexError):
        return ""


def _priority_flags(fields: list[str]) -> str:
    """
    Helper:
    Returns priority flags based on the nice value.

    Args:
        fields (list[str]): Fields from /proc/<pid>/stat.

    Returns:
        str: '<' for high priority, 'N' for low priority, or '' otherwise.
    """

    try:
        nice = int(fields[ProcessStateIndex.NICE])
        if nice < StatMapIndex.DEFAULT_PRIORITY:
            return StatMapIndex.FLAG_MAP["high_priority"]
        if nice > StatMapIndex.DEFAULT_PRIORITY:
            return StatMapIndex.FLAG_MAP["low_priority"]
    except (ValueError, IndexError):
        pass
    return ""


def _multi_threaded_flag(fields: list[str]) -> str:
    """
    Helper:
    Returns 'l' if the process has more than 1 thread.

    Args:
        fields (list[str]): Fields from /proc/<pid>/stat.

    Returns:
        str: 'l' if multi-threaded, otherwise ''.
    """

    try:
        nthreads = int(fields[ProcessStateIndex.NLWP])
        if nthreads > StatMapIndex.MULTHREAD_THRESH:
            return StatMapIndex.FLAG_MAP["multi_threaded"]
    except (ValueError, IndexError):
        pass
    return ""


def _locked_flag(fields: list[str]) -> str:
    """
    Helper:
    Returns 'L' if the process has locked memory pages.

    Args:
        fields (list[str]): Fields from /proc/<pid>/stat.

    Returns:
        str: 'L' if memory locked, otherwise ''.
    """

    try:
        locked = int(fields[ProcessStateIndex.LOCKED])
        if locked > StatMapIndex.LOCKED_THRESH:
            return StatMapIndex.FLAG_MAP["locked"]
    except (ValueError, IndexError):
        pass
    return ""


def _foreground_flag(fields: list[str]) -> str:
    """
    Helper:
    Returns '+' if the process is in the foreground process group of its terminal.

    Args:
        fields (list[str]): Fields from /proc/<pid>/stat.

    Returns:
        str: '+' if foreground process, otherwise ''.
    """

    try:
        tty_nr = int(fields[ProcessStateIndex.TTY_NR])
        if tty_nr <= 0:
            return ""

        tty_name = read_tty_nr_to_name(tty_nr)
        tty_path = f"/dev/{tty_name}"

        fd = os.open(tty_path, os.O_RDONLY)
        try:
            fg_pgrp = os.tcgetpgrp(fd)
        finally:
            os.close(fd)

        pgrp = int(fields[ProcessStateIndex.PGRP])
        return StatMapIndex.FLAG_MAP["foreground"] if pgrp == fg_pgrp else ""
    except (OSError, IndexError, ValueError):
        return ""


def get_process_stat(pid: int) -> str:
    """
    Returns the human-readable STAT string for a process, including
    base state and flags (session leader, priority, memory lock, threads, foreground).

    Uses caching for sleeping, disk sleep, or zombie processes.

    Args:
        pid (int): Process ID.

    Returns:
        str: Combined STAT string, or default if the process cannot be read.
    """

    fields = read_process_stat_fields(pid)
    if not fields:
        return StatMapIndex.DEFAULT_STAT

    state_char = base_state(fields)

    # Use cache for sleeping, disk sleep, or zombie processes
    if state_char in ("S", "D", "Z") and pid in _STAT_CACHE:
        cached = _STAT_CACHE[pid]
        return f"{state_char}{cached[1:]}"  # keep cached flags, update base state

    flags = (
        _session_leader_flag(fields, pid)
        + _priority_flags(fields)
        + _locked_flag(fields)
        + _multi_threaded_flag(fields)
    )
    fg_flag = _foreground_flag(fields) if state_char == "R" else ""

    stat_str = state_char + flags + fg_flag
    _STAT_CACHE[pid] = stat_str
    return stat_str
