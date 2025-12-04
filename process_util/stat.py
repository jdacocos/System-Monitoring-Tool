"""
stat.py

This module provides functions for retrieving and interpreting process
state information from the Linux /proc/<pid>/stat files. It converts
raw kernel process states and flags into human-readable strings,
similar to the STAT column in the `ps` command.

Functions include helpers for:
    - Reading and splitting /proc/<pid>/stat
    - Extracting base process state
    - Detecting session leader processes
    - Determining high/low priority via nice values
    - Flagging multi-threaded processes
    - Detecting locked memory pages
    - Detecting foreground processes

All functions handle missing or inaccessible process files gracefully,
returning default values when necessary.
"""

import os
from process_constants import ProcessStateIndex, StatMapIndex
from process_util.tty import read_tty_nr_to_name
from file_helpers import read_file

# Simple PID -> stat cache
_STAT_CACHE: dict[int, str] = {}


def read_process_stat_fields(pid: int) -> list[str]:
    """Read /proc/<pid>/stat and return fields as a list of strings."""
    stat_path = f"/proc/{pid}/stat"
    content = read_file(stat_path)
    if not content:
        print(f"[WARN] Could not read {stat_path}")
        return []
    return content.split()


def _base_state(fields: list[str]) -> str:
    """Return the main process state character (R, S, D, etc.)."""
    try:
        return StatMapIndex.STATE_MAP.get(
            fields[ProcessStateIndex.STATE], StatMapIndex.DEFAULT_STAT
        )
    except IndexError:
        return StatMapIndex.DEFAULT_STAT


def _session_leader_flag(fields: list[str], pid: int) -> str:
    """Return 's' if process is a session leader."""
    try:
        return (
            StatMapIndex.FLAG_MAP["session_leader"]
            if int(fields[ProcessStateIndex.SESSION]) == pid
            else ""
        )
    except (ValueError, IndexError):
        return ""


def _priority_flags(fields: list[str]) -> str:
    """Return '<' or 'N' if process is high or low priority based on nice value."""
    try:
        nice = int(fields[ProcessStateIndex.NICE])
        if nice < StatMapIndex.DEFAULT_PRIORITY:
            return StatMapIndex.FLAG_MAP["high_priority"]
        elif nice > StatMapIndex.DEFAULT_PRIORITY:
            return StatMapIndex.FLAG_MAP["low_priority"]
    except (ValueError, IndexError):
        pass
    return ""


def _multi_threaded_flag(fields: list[str]) -> str:
    """Return 'l' if process has more than 1 thread."""
    try:
        nthreads = int(fields[ProcessStateIndex.NLWP])
        if nthreads > StatMapIndex.MULTHREAD_THRESH:
            return StatMapIndex.FLAG_MAP["multi_threaded"]
    except (ValueError, IndexError):
        pass
    return ""


def _locked_flag(fields: list[str]) -> str:
    """Return 'L' if process has locked memory pages."""
    try:
        locked = int(fields[ProcessStateIndex.LOCKED])
        if locked > StatMapIndex.LOCKED_THRESH:
            return StatMapIndex.FLAG_MAP["locked"]
    except (ValueError, IndexError):
        pass
    return ""


def _foreground_flag(fields: list[str]) -> str:
    """Return '+' if process is in the foreground process group of its terminal."""
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
    Return human-readable process stat string with caching for sleeping processes.
    Combines base state and flags for session, priority, locked memory, threads, and foreground.
    """
    fields = read_process_stat_fields(pid)
    if not fields:
        return StatMapIndex.DEFAULT_STAT

    base_state = _base_state(fields)

    # Use cache for sleeping, disk sleep, or zombie processes
    if base_state in ("S", "D", "Z") and pid in _STAT_CACHE:
        cached = _STAT_CACHE[pid]
        return f"{base_state}{cached[1:]}"  # keep cached flags, update base state

    flags = (
        _session_leader_flag(fields, pid)
        + _priority_flags(fields)
        + _locked_flag(fields)
        + _multi_threaded_flag(fields)
    )
    fg_flag = _foreground_flag(fields) if base_state == "R" else ""

    stat_str = base_state + flags + fg_flag
    _STAT_CACHE[pid] = stat_str
    return stat_str
