"""
vsz.py

This module provides a function to retrieve the virtual memory size (VSZ)
of a process on a Linux system, corresponding to the VSZ column in `ps aux`.

Functions:
    get_process_vsz(pid: int) -> int:
        Returns the VSZ of the given process in KB.

Usage Example:
    from process_util.vsz import get_process_vsz

    pid = 1234
    vsz_kb = get_process_vsz(pid)
    print(f"Process {pid} VSZ: {vsz_kb} KB")
"""

import os
from process_constants import LNX_FS, RD_ONLY, UTF_8, ProcessStateIndex, ProcStatmIndex


def get_process_vsz(pid: int) -> int:
    """
    Returns the virtual memory size (VSZ) of a process in KB.

    Parameters:
        pid (int): Process ID

    Returns:
        int: VSZ in KB, or 0 if process cannot be read.
    """
    vsz_kb = 0
    stat_path = f"/proc/{pid}/stat"

    try:
        with open(stat_path, RD_ONLY, encoding=UTF_8) as f:
            fields = f.read().split()
            if len(fields) > ProcessStateIndex.VSZ:
                try:
                    vsz_bytes = int(fields[ProcessStateIndex.VSZ])
                    vsz_kb = vsz_bytes // ProcStatmIndex.BYTES_TO_KB
                except ValueError as e:
                    print(f"[ERROR] Invalid VSZ value for PID {pid}: {e}")
            else:
                print(f"[WARN] Not enough fields in {stat_path} to read VSZ")
    except FileNotFoundError:
        print(f"[ERROR] Process {pid} stat file not found: {stat_path}")
    except PermissionError:
        print(f"[ERROR] Permission denied when reading {stat_path}")
    return vsz_kb
