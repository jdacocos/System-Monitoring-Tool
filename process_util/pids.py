"""
process_util

A modular Linux process inspection package backed by the /proc file system.

Each module in this package is dedicated to retrieving *one* specific
attribute of a process (PID, CPU%, memory usage, runtime, owner, etc.).
This design promotes separation of concerns, testability, and
maintainability.

These utilities are intended to be composed by the ProcessInfo
dataclass in process.py, forming a complete snapshot of a process
similar to the output of 'ps aux'.

Only Python standard library os is used.
"""

import os
from typing import Iterator
from process_constants import LNX_FS


def open_file_system(path=LNX_FS) -> Iterator[os.DirEntry]:
    """
    Return an iterator over entries in the /proc file system.

    If the path cannot be opened, an empty iterator is returned.
    """
    try:
        return os.scandir(path)
    except FileNotFoundError:
        return iter([])


def get_process_pids() -> list[int]:
    """
    Return a list of all running process IDs (PIDs) found in /proc.
    """
    pids: list[int] = []
    with open_file_system() as entries:
        for entry in entries:
            if entry.name.isdigit():
                pids.append(int(entry.name))
    return pids
