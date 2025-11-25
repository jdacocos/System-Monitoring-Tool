"""
rss.py

This module provides functions for retrieving the resident set size (RSS) of
processes and total system memory on a Linux system. RSS is the portion of
a process's memory that is held in RAM, excluding swapped-out pages.

Functions:
    _read_meminfo_total(): Read total system memory from /proc/meminfo.
    get_process_rss(pid: int): Retrieve the RSS of a given process in KB.

The module only uses standard libraries: os, typing, and built-in file I/O.
"""

import os
from process_constants import RD_ONLY, UTF_8, MemInfoIndex, ProcStatmIndex


def _read_meminfo_total() -> int:
    """
    Helper:
    Reads the total system memory in KB from /proc/meminfo.

    Returns:
        int: Total memory in KB, or 0 if the value could not be read.
    """
    mem_total_kb = 0
    meminfo_path = "/proc/meminfo"

    try:
        with open(meminfo_path, RD_ONLY, encoding=UTF_8) as meminfo_file:
            for line in meminfo_file:
                if line.startswith(MemInfoIndex.MEMTOTAL_LABEL):
                    fields = line.split()
                    if len(fields) > MemInfoIndex.MEMTOTAL_VALUE:
                        try:
                            mem_total_kb = int(fields[MemInfoIndex.MEMTOTAL_VALUE])
                        except ValueError:
                            print(
                                f"Warning: Could not convert MemTotal value "
                                f"to int: {fields[MemInfoIndex.MEMTOTAL_VALUE]}"
                            )
                    break
    except FileNotFoundError:
        print(f"Error: {meminfo_path} not found.")
    except PermissionError:
        print(f"Error: Permission denied reading {meminfo_path}.")
    return mem_total_kb


def get_process_rss(pid: int) -> int:
    """
    Returns the resident set size (RSS) of a process in KB.
    RSS is the portion of a process's memory held in RAM, not including swapped-out pages.

    Parameters:
        pid (int): Process ID

    Returns:
        int: RSS in KB, or 0 if the process does not exist or cannot be read.
    """
    rss_kb = 0
    statm_path = f"/proc/{pid}/statm"

    try:
        with open(statm_path, RD_ONLY, encoding=UTF_8) as statm_file:
            fields = statm_file.read().split()
            if len(fields) > ProcStatmIndex.RSS:
                try:
                    page_size_kb = (
                        os.sysconf("SC_PAGESIZE") // ProcStatmIndex.BYTES_TO_KB
                    )
                    rss_pages = int(fields[ProcStatmIndex.RSS])
                    rss_kb = rss_pages * page_size_kb
                except ValueError:
                    print(
                        f"Warning: Could not convert RSS value to int for PID {pid}: "
                        f"{fields[ProcStatmIndex.RSS]}"
                    )
                except AttributeError:
                    print("Warning: os.sysconf not supported on this system.")
    except FileNotFoundError:
        print(f"Error: {statm_path} not found.")
    except PermissionError:
        print(f"Error: Permission denied reading {statm_path}.")

    return rss_kb
