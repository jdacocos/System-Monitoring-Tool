"""
process_util.py

This module provides functions for retrieving process information
on a Linux system, including CPU and memory usage percentages,
user ownership, and PID listing.

It only uses standard libraries: os, time, and typing.
"""
import os
import time
from typing import Iterator

from process_constants import (
    ProcessStateIndex, CpuStatIndex, PasswdIndex, MemInfoIndex, ProcStatmIndex
    )

LNX_FS = '/proc'

def open_file_system(path=LNX_FS) -> Iterator[os.DirEntry]:
    """
    Open a directory iterator to the /proc file system.
    """
    try:
        return os.scandir(path)
    except FileNotFoundError:
        print(f"Unable to open {path}")


def get_process_pids() -> list[int]:
    """
    Retrieves all PIDs from /proc.
    """
    pids = []
    with open_file_system() as entries:
        for entry in entries:
            if entry.name.isdigit():
                pids.append(int(entry.name))
    return pids

def _uid_to_username(uid: int) -> str | None:
    """
    Helper: Convert a UID to a username using /etc/passwd.

    Parameters:
        uid (int): User ID to look up

    Returns:
        str | None: Username if found, otherwise None.
    """
    username = None
    passwd_path = "/etc/passwd"

    try:
        with open(passwd_path, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) <= PasswdIndex.UID:
                    continue
                try:
                    entry_uid = int(parts[PasswdIndex.UID])
                except ValueError:
                    print(f"Warning: Invalid UID in {passwd_path}: {parts[PasswdIndex.UID]}")
                    continue
                if entry_uid == uid:
                    username = parts[PasswdIndex.NAME]
                    break
    except FileNotFoundError:
        print(f"Error: {passwd_path} not found. Cannot resolve UID {uid}.")
    except PermissionError:
        print(f"Error: Permission denied while reading {passwd_path}. "
              f"Cannot resolve UID {uid}.")
    return username

def get_process_user(pid: int) -> str | None:
    """
    Retrieve the username that owns a given process.

    Parameters:
        pid (int): Process ID

    Returns:
        str | None: Username if found, otherwise None.
    """
    
    proc_path = f"/proc/{pid}"
    username: str | None = None

    try:
        # Get file status of the process directory to retrieve UID
        proc_stat = os.stat(proc_path)
        process_uid = proc_stat.st_uid

        # Convert UID to username
        username = _uid_to_username(process_uid)
        
    except FileNotFoundError:
        print(f"Error: Process directory {proc_path} not found. PID {pid} may not exist.")
    except PermissionError:
        print(f"Error: Permission denied accessing {proc_path}. "
              f"Cannot determine owner of PID {pid}.")
    return username

def _read_proc_stat_total() -> int:
    """
    Helper: Retrieve total CPU jiffies from /proc/stat.
    Jiffy - basic unit of time Linux kernel uses to measure CPU activity.

    Returns:
        int: Total CPU jiffies (sum of USER, NICE, SYSTEM, IDLE),
             or 0 if /proc/stat cannot be read.
    """
    stat_path = "/proc/stat"
    total_jiffies = 0

    try:
        with open(stat_path, "r") as f:
            first_line = f.readline()
            if first_line.startswith("cpu "):
                # skip the "cpu" label
                cpu_fields = first_line.split()[CpuStatIndex.CPU_LABEL_COLUMN:]

                # Sum USER + NICE + SYSTEM + IDLE (indexes defined in CpuStatIndex)
                total_jiffies = sum(int(cpu_fields[i]) for i in range(CpuStatIndex.IDLE + 1))

    except FileNotFoundError:
        print(f"Error: {stat_path} not found. Cannot read total CPU jiffies.")
    except IndexError:
        print(f"Error: Unexpected format in {stat_path}. Not enough CPU fields.")
    except ValueError:
        print(f"Error: Invalid numeric value found in {stat_path}.")
    return total_jiffies

def _read_proc_pid_time(pid: int) -> int:
    """
    Helper: Retrieve total CPU jiffies used by a process (utime + stime)
    from /proc/<pid>/stat.

    Parameters:
        pid (int): Process ID

    Returns:
        int: Total CPU jiffies for the process, or 0 if process
             does not exist or cannot be read.
    """
    stat_path = f"/proc/{pid}/stat"
    total_proc_jiffies = 0

    try:
        with open(stat_path, "r") as f:
            fields = f.read().split()

            # Ensure required fields exist
            if len(fields) > ProcessStateIndex.STIME:
                utime = int(fields[ProcessStateIndex.UTIME])
                stime = int(fields[ProcessStateIndex.STIME])
                total_proc_jiffies = utime + stime

    except FileNotFoundError:
        print(f"Error: {stat_path} not found. Process may have exited.")
    except IndexError:
        print(f"Error: Unexpected format in {stat_path}. Not enough fields.")
    except ValueError:
        print(f"Error: Invalid numeric value in {stat_path} for utime/stime.")

    return total_proc_jiffies

def get_process_cpu_percent(pid: int, interval: float = 0.1) -> float:
    """
    Calculate the CPU usage percentage of a process over a given interval.

    Parameters:
        pid (int): Process ID
        interval (float): Time interval (seconds) between samples

    Returns:
        float: CPU usage percentage (0.0 - 100.0), or CPU_PERCENT_INVALID if
               the calculation could not be performed.
    """
    # read initial CPU jiffies
    proc_jiffies_start = _read_proc_pid_time(pid)
    total_jiffies_start = _read_proc_stat_total()

    time.sleep(interval)

    # read CPU jiffies after time pass
    proc_jiffies_end = _read_proc_pid_time(pid)
    total_jiffies_end = _read_proc_stat_total()

    delta_proc = proc_jiffies_end - proc_jiffies_start
    delta_total = total_jiffies_end - total_jiffies_start

    # check division by zero
    if delta_total <= CpuStatIndex.MIN_DELTA_TOTAL:
        print(f"Warning: Total jiffies delta too small ({delta_total}).")
        return CpuStatIndex.CPU_PERCENT_INVALID

    cpu_percent = (delta_proc / delta_total) * CpuStatIndex.CPU_PERCENT_SCALE
    return round(cpu_percent, CpuStatIndex.CPU_PERCENT_ROUND_DIGITS)

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
        with open(meminfo_path, "r") as meminfo_file:
            for line in meminfo_file:
                if line.startswith(MemInfoIndex.MEMTOTAL_LABEL):
                    fields = line.split()
                    if len(fields) > MemInfoIndex.MEMTOTAL_VALUE:
                        try:
                            mem_total_kb = int(fields[MemInfoIndex.MEMTOTAL_VALUE])
                        except ValueError:
                            print(f"Warning: Could not convert MemTotal value "
                                  f"to int: {fields[MemInfoIndex.MEMTOTAL_VALUE]}")
                    break
    except FileNotFoundError:
        print(f"Error: {meminfo_path} not found.")
    except PermissionError:
        print(f"Error: Permission denied reading {meminfo_path}.")
    return mem_total_kb

def _read_proc_rss(pid: int) -> int:
    """
    Helper: 
    Reads the resident set size (RSS) in KB of a process from /proc/<pid>/statm.
    RSS is the portion of a process's memory held in RAM, not including swapped-out pages.

    Parameters:
        pid (int): Process ID

    Returns:
        int: RSS in KB, or 0 if the process does not exist or cannot be read. 
    """
    rss_kb = 0
    statm_path = f"/proc/{pid}/statm"

    try:
        with open(statm_path, "r") as statm_file:
            fields = statm_file.read().split()
            if len(fields) > ProcStatmIndex.RSS:
                try:
                    page_size_kb = os.sysconf("SC_PAGESIZE") // ProcStatmIndex.BYTES_TO_KB
                    rss_pages = int(fields[ProcStatmIndex.RSS])
                    rss_kb = rss_pages * page_size_kb
                except ValueError:
                    print(f"Warning: Could not convert RSS value to int"
                          f"for PID {pid}: {fields[ProcStatmIndex.RSS]}")
                except AttributeError:
                    print("Warning: os.sysconf not supported on this system.")
    except FileNotFoundError:
        print(f"Error: {statm_path} not found.")
    except PermissionError:
        print(f"Error: Permission denied reading {statm_path}.")

    return rss_kb

def get_process_mem_percent(pid: int) -> float:
    """
    Calculate the memory usage percentage of a process.

    Parameters:
        pid (int): Process ID

    Returns:
        float: Memory usage percent (0.0 - 100.0)
    """
    rss_kb = _read_proc_rss(pid)
    total_mem_kb = _read_meminfo_total()

    # check division by zero or invalid total memory
    if total_mem_kb <= MemInfoIndex.MEM_INVALID:
        print(f"Warning: Total system memory invalid or unreadable for PID {pid}.")
        return float(MemInfoIndex.MEM_INVALID)

    mem_percent = (rss_kb / total_mem_kb) * MemInfoIndex.MEM_PERCENT_SCALE
    return round(mem_percent, MemInfoIndex.MEM_PERCENT_ROUND_DIGITS)
