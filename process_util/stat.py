"""
stat.py

This module provides functions for retrieving and interpreting process
state information from the Linux /proc/<pid>/stat files. It converts
raw kernel process states and flags into human-readable strings,
similar to the STAT column in the `ps` command.

The module includes helpers for:

    - Reading and splitting the /proc/<pid>/stat file
    - Extracting the base process state (R, S, D, etc.)
    - Detecting session leader processes
    - Determining high/low priority via nice values
    - Flagging multi-threaded processes
    - Detecting locked memory pages

All functions handle missing or inaccessible process files gracefully,
returning default values when necessary.

Requirements:
    - Standard Python libraries: os, typing
"""

import os
from process_constants import RD_ONLY, UTF_8, ProcessStateIndex, StatMapIndex
from process_util.tty import _read_tty_nr_to_name

# Simple PID → stat cache
_STAT_CACHE: dict[int, str] = {}


def _read_process_stat_fields(pid: int) -> list[str]:
    """
    Helper:
    Reads and splits the contents of /proc/<pid>/stat into fields.

    Parameters:
        pid (int): Process ID

    Returns:
        list[str]: List of fields from /proc/<pid>/stat, or empty list on error
    """
    stat_path = f"/proc/{pid}/stat"
    fields: list[str] = []
    try:
        with open(stat_path, RD_ONLY, encoding=UTF_8) as f:
            fields = f.read().split()
    except FileNotFoundError:
        print(f"[ERROR] Process {pid} stat file not found: {stat_path}")
    except PermissionError:
        print(f"[ERROR] Permission denied reading {stat_path}")
    except OSError as e:
        print(f"[ERROR] Unexpected OS error reading {stat_path}: {e}")
    return fields


def _interpret_process_state(fields: list[str], pid: int) -> str:
    """
    Helper:
    Converts /proc/<pid>/stat fields into a human-readable process stat string,
    combining the kernel state and any applicable flags such as session leader,
    priority, locked pages, or multi-threaded indicators.

    Parameters:
        fields (list[str]): Fields from /proc/<pid>/stat
        pid (int): Process ID

    Returns:
        str: Human-readable stat string (e.g., 'Ss<l') or DEFAULT_STAT
    """
    unknown_stat: str = StatMapIndex.DEFAULT_STAT
    if len(fields) <= ProcessStateIndex.STATE:
        print("[WARN] Not enough fields to read process state")
        return unknown_stat

    # Base kernel state
    stat_str = StatMapIndex.STATE_MAP.get(fields[ProcessStateIndex.STATE], unknown_stat)

    # Append session leader flag
    stat_str += _session_leader_flag(fields, pid)

    # Append high/low priority flags
    stat_str += _priority_flags(fields)

    # Append locked memory flag
    stat_str += _locked_flag(fields)

    # Append multi-threaded flag
    stat_str += _multi_threaded_flag(fields)

    # Append foreground flag
    stat_str += _foreground_flag(fields)

    return stat_str


def _base_state(fields: list[str]) -> str:
    """
    Helper:
    Return the main process state character (R, S, D, etc.).
    """
    return StatMapIndex.STATE_MAP.get(
        fields[ProcessStateIndex.STATE], StatMapIndex.DEFAULT_STAT
    )


def _session_leader_flag(fields: list[str], pid: int) -> str:
    """
    Helper:
    Return 's' if the process is a session leader.
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
    Return '<' or 'N' if process is high or low priority according to nice value.
    """
    flags_str = ""
    try:
        nice = int(fields[ProcessStateIndex.NICE])
        if nice < StatMapIndex.DEFAULT_PRIORITY:
            flags_str += StatMapIndex.FLAG_MAP["high_priority"]
        elif nice > StatMapIndex.DEFAULT_PRIORITY:
            flags_str += StatMapIndex.FLAG_MAP["low_priority"]
    except (ValueError, IndexError):
        pass
    return flags_str


def _multi_threaded_flag(fields: list[str]) -> str:
    """
    Helper:
    Return 'l' if the process has more than 1 thread.
    """

    try:
        nthreads = int(fields[ProcessStateIndex.NLWP])
        return (
            StatMapIndex.FLAG_MAP["multi_threaded"]
            if nthreads > StatMapIndex.MULTHREAD_THRESH
            else ""
        )
    except (ValueError, IndexError):
        return ""


def _locked_flag(fields: list[str]) -> str:
    """
    Helper:
    Return 'L' if the process has locked memory pages.
    """

    try:
        locked = int(fields[ProcessStateIndex.LOCKED])
        return (
            StatMapIndex.FLAG_MAP["locked"]
            if locked > StatMapIndex.LOCKED_THRESH
            else ""
        )
    except (ValueError, IndexError):
        return ""


def _foreground_flag(fields: list[str]) -> str:
    """
    Return '+' if the process is in the foreground process group of its terminal.
    Safely handles processes without TTY or inaccessible TTY.
    """
    try:
        tty_nr = int(fields[ProcessStateIndex.TTY_NR])
        if tty_nr <= 0:
            return ""

        tty_name = _read_tty_nr_to_name(tty_nr)
        tty_path = f"/dev/{tty_name}"

        # Safely open tty; skip if not allowed
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
    """Return human-readable process stat string with caching for sleeping processes."""
    fields = _read_process_stat_fields(pid)
    if not fields:
        return StatMapIndex.DEFAULT_STAT

    base_state = _base_state(fields)

    # Use cache for sleeping, disk sleep, or zombie
    if base_state in ("S", "D", "Z") and pid in _STAT_CACHE:
        cached = _STAT_CACHE[pid]
        return f"{base_state}{cached[1:]}"  # keep cached flags, update base state

    # Compute flags
    flags = (
        _session_leader_flag(fields, pid)
        + _priority_flags(fields)
        + _locked_flag(fields)
        + _multi_threaded_flag(fields)
    )
    fg = _foreground_flag(fields) if base_state == "R" else ""

    stat_str = base_state + flags + fg
    _STAT_CACHE[pid] = stat_str

    return stat_str
