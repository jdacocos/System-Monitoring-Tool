"""
pids.py

This module provides functions for retrieving process IDs (PIDs) on a Linux
system using the /proc filesystem.

Functions:
    get_process_pids() -> list[int]
        Returns a list of all currently running process IDs.

Only Python standard libraries and helpers from file_helper.py are used.
"""

import os
from typing import Iterator
from file_helpers import read_lines


def get_process_pids(proc_path: str = "/proc") -> list[int]:
    """
    Return a list of all running process IDs (PIDs) found in /proc.

    Parameters:
        proc_path (str): Path to the proc filesystem. Defaults to "/proc".

    Returns:
        list[int]: List of PIDs as integers. Returns empty list if /proc cannot be read.
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
