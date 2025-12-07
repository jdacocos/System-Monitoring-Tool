"""
rss.py

This module provides functions to retrieve the resident set size (RSS) of
processes and total system memory on a Linux system. RSS represents the
portion of a process's memory held in RAM, excluding swapped-out pages.

Shows:
- Reading total system memory from /proc/meminfo
- Retrieving per-process RSS from /proc/<pid>/statm
- Handling missing files, permission errors, and invalid values gracefully

Dependencies:
- Standard Python library: os
- backend.file_helpers for safe file reading
- backend.process_constants for field indices
"""

import os
from backend.process_constants import MemInfoIndex, ProcStatmIndex
from backend.file_helpers import read_file


def read_meminfo_total() -> int:
    """
    Reads the total system memory in KB from /proc/meminfo.

    Returns:
        int: Total memory in KB, or 0 if the value could not be read.
    """
    mem_total_kb = 0
    meminfo_path = "/proc/meminfo"
    meminfo_content: str | None = read_file(meminfo_path)

    if not meminfo_content:
        print(f"Warning: {meminfo_path} could not be read")
        return mem_total_kb

    for line in meminfo_content.splitlines():
        if line.startswith(MemInfoIndex.MEMTOTAL_LABEL):
            fields = line.split()
            if len(fields) > MemInfoIndex.MEMTOTAL_VALUE:
                try:
                    mem_total_kb = int(fields[MemInfoIndex.MEMTOTAL_VALUE])
                except ValueError:
                    print(
                        f"Warning: Could not convert MemTotal value "
                        f"to int in {meminfo_path}: {fields[MemInfoIndex.MEMTOTAL_VALUE]}"
                    )
            break
    else:
        print(f"Warning: MemTotal not found in {meminfo_path}")

    return mem_total_kb


def get_process_rss(pid: int) -> int:
    """
    Retrieves the resident set size (RSS) of a process in KB.

    Args:
        pid (int): Process ID.

    Returns:
        int: RSS in KB for the process.
             Returns 0 if the process does not exist, cannot be read, or an error occurs.
    """

    rss_kb = 0
    statm_content: str | None = read_file(f"/proc/{pid}/statm")

    if statm_content:
        fields = statm_content.split()
        if len(fields) > ProcStatmIndex.RSS:
            try:
                page_size_kb = os.sysconf("SC_PAGESIZE") // ProcStatmIndex.BYTES_TO_KB
                rss_pages = int(fields[ProcStatmIndex.RSS])
                rss_kb = rss_pages * page_size_kb
            except ValueError:
                print(
                    f"Warning: Could not convert RSS value to int for PID {pid}: "
                    f"{fields[ProcStatmIndex.RSS]}"
                )
            except AttributeError:
                print("Warning: os.sysconf not supported on this system.")
    else:
        print(f"Warning: /proc/{pid}/statm could not be read")

    return rss_kb
