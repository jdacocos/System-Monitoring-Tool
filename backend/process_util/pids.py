"""
pids.py

This module provides functionality to retrieve process IDs (PIDs) on a Linux system
by reading the /proc filesystem.

Shows:
- Retrieving all currently running process IDs
- Filtering numeric entries in /proc to identify valid PIDs
- Graceful handling of missing or inaccessible /proc directories

Dependencies:
- Standard Python library: os
"""


import os


def get_process_pids(proc_path: str = "/proc") -> list[int]:
    """
    Returns a list of all currently running process IDs (PIDs).

    Args:
        proc_path (str): Path to the proc filesystem. Defaults to "/proc".

    Returns:
        list[int]: List of PIDs as integers.
                   Returns an empty list if /proc cannot be read or is inaccessible.
    """

    pids: list[int] = []

    try:
        entries = os.listdir(proc_path)
        for entry in entries:
            if entry.isdigit():
                pids.append(int(entry))
    except (FileNotFoundError, PermissionError) as e:
        print(f"Warning: Cannot read {proc_path}: {e}")

    return pids
