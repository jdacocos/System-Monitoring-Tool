"""
tty.py

This module provides functions to retrieve the terminal (TTY) associated
with a process on a Linux system.

Functions include:

    - _read_tty_nr_to_name: Convert a numeric TTY number from /proc/<pid>/stat
      into a human-readable TTY name.
    - get_process_tty: Retrieve the TTY name for a given process, returning
      a default value if unavailable.

It relies on the /proc filesystem and a predefined TTY map.

Requirements:
    Standard Python libraries only: os, typing
"""

from process_constants import RD_ONLY, UTF_8, ProcessStateIndex, TTYMapIndex


def _read_tty_nr_to_name(tty_nr: int) -> str:
    """
    Helper:
    Convert numeric tty_nr to a readable TTY name.

    Parameters:
        tty_nr (int): TTY number from /proc/<pid>/stat

    Returns:
        str: TTY name (e.g., 'pts/0', 'tty1') or DEFAULT_TTY if invalid/unrecognized
    """
    if tty_nr <= 0:
        return TTYMapIndex.DEFAULT_TTY

    # Extract major/minor device numbers using constants
    major = (tty_nr >> TTYMapIndex.MAJOR_SHIFT) & TTYMapIndex.MAJOR_MASK
    minor = (tty_nr & TTYMapIndex.MINOR_LOW_MASK) | (
        (tty_nr >> TTYMapIndex.MINOR_HIGH_SHIFT) & TTYMapIndex.MINOR_HIGH_MASK
    )

    # Map common major numbers to tty types
    if major == TTYMapIndex.MAJOR_VT:
        return f"tty{minor}"

    if major == TTYMapIndex.MAJOR_PTS:
        return f"pts/{minor}"

    # Fallback for unknown major numbers
    return TTYMapIndex.DEFAULT_TTY


def get_process_tty(pid: int) -> str:
    """
    Returns the readable TTY name for a given process.

    Parameters:
        pid (int): Process ID

    Returns:
        str: TTY name (e.g., 'pts/0', 'tty1') or DEFAULT_TTY if unavailable
    """
    tty_name = TTYMapIndex.DEFAULT_TTY
    stat_path = f"/proc/{pid}/stat"

    try:
        with open(stat_path, RD_ONLY, encoding=UTF_8) as stat_file:
            fields = stat_file.read().split()
            if len(fields) > ProcessStateIndex.TTY_NR:
                try:
                    tty_nr = int(fields[ProcessStateIndex.TTY_NR])
                    tty_name = _read_tty_nr_to_name(tty_nr)
                except ValueError:
                    print(
                        f"[WARN] Invalid TTY_NR value for "
                        f"PID {pid}: {fields[ProcessStateIndex.TTY_NR]}"
                    )
            else:
                print(f"[WARN] Not enough fields in {stat_path} to read TTY_NR")
    except FileNotFoundError:
        print(f"[ERROR] Process {pid} stat file not found: {stat_path}")
    except PermissionError:
        print(f"[ERROR] Permission denied reading {stat_path}")

    return tty_name
