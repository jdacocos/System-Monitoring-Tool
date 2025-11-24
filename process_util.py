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
    Returns None if UID is not found.
    """
    username = None
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) <= PasswdIndex.UID:
                    continue
                try:
                    entry_uid = int(parts[PasswdIndex.UID])
                except ValueError:
                    continue
                if entry_uid == uid:
                    username = parts[PasswdIndex.NAME]
                    break
    except (FileNotFoundError, PermissionError):
        pass
    return username


def get_process_user(pid: int) -> str | None:
    """
    Returns the username owning the process.
    Only uses the os module.
    """
    proc_path = f"/proc/{pid}"
    username = None
    try:
        stat_info = os.stat(proc_path)
        uid = stat_info.st_uid
        username = _uid_to_username(uid)
    except FileNotFoundError:
        pass
    return username


def _read_proc_stat_total() -> int:
    """
    Helper: Retrieves total CPU jiffies from /proc/stat.
    Jiffy - basic unit of time Linux kernel uses to measure CPU activity.
    """
    total_jiffies = 0
    try:
        with open("/proc/stat", "r") as f:
            line = f.readline()
            if line.startswith("cpu "):
                fields = line.split()[CpuStatIndex.CPU_LABEL_COLUMN:]
                # sum USER + NICE + SYSTEM + IDLE
                total_jiffies = sum(int(fields[i]) for i in range(CpuStatIndex.IDLE + 1))
    except (FileNotFoundError, IndexError, ValueError):
        pass
    return total_jiffies


def _read_proc_pid_time(pid: int) -> int:
    """
    Helper: Returns total CPU jiffies used by a process (utime + stime)
    by reading /proc/<pid>/stat.
    """
    total_proc_jiffies = 0
    stat_path = f"/proc/{pid}/stat"

    try:
        with open(stat_path, "r") as f:
            fields = f.read().split()
            # ensure fields exist
            if len(fields) > ProcessStateIndex.STIME:
                utime = int(fields[ProcessStateIndex.UTIME])
                stime = int(fields[ProcessStateIndex.STIME])
                total_proc_jiffies = utime + stime
    except (FileNotFoundError, IndexError, ValueError):
        pass

    return total_proc_jiffies

def get_process_cpu_percent(pid: int, interval: float = 0.1) -> float:
    """
    Calculate the CPU usage percentage of a process.    
    
    Parameters:
        pid (int): Process ID
        interval (float): Time interval (seconds) between samples for calculation

    Returns:
        float: CPU usage percentage (0.0 - 100.0)
    """
    
    # Read initial jiffies
    proc_jiffies_1 = _read_proc_pid_time(pid)
    total_jiffies_1 = _read_proc_stat_total()

    time.sleep(interval)

    # Read jiffies again
    proc_jiffies_2 = _read_proc_pid_time(pid)
    total_jiffies_2 = _read_proc_stat_total()

    # Compute differences
    delta_proc = proc_jiffies_2 - proc_jiffies_1
    delta_total = total_jiffies_2 - total_jiffies_1

    # Avoid division by zero
    if delta_total <= CpuStatIndex.MIN_DELTA_TOTAL:
        return CpuStatIndex.CPU_PERCENT_INVALID

    cpu_percent = (delta_proc / delta_total) * CpuStatIndex.CPU_PERCENT_SCALE
    return round(cpu_percent, CpuStatIndex.CPU_PERCENT_ROUND_DIGITS)

def _read_meminfo_total() -> int:
    """
    Helper:
    Reads total system memory in KB from /proc/meminfo.

    Returns:
        int: total memory in KB, or 0 if not found.
    """
    mem_total = 0
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith(MemInfoIndex.MEMTOTAL_LABEL):
                    parts = line.split()
                    if len(parts) > MemInfoIndex.MEMTOTAL_VALUE:
                        try:
                            mem_total = int(parts[MemInfoIndex.MEMTOTAL_VALUE])
                        except ValueError:
                            pass
                    break
    except (FileNotFoundError, PermissionError):
        pass
    return mem_total

def _read_proc_rss(pid: int) -> int:
    """
    Helper: 
    Reads the resident set size (RSS) in KB of a process from /proc/<pid>/statm.
    RSS is the process's memory that is held in RAM, not including swapped-out pages.

    Returns:
        int: RSS in KB, or 0 if process does not exist or cannot be read. 
    """

    res_kb = 0
    statm_path = f"/proc/{pid}/statm"
    try:
        with open(statm_path, "r") as f:
            fields = f.read().split()
            if len(fields) > ProcStatmIndex.RSS:
                try:
                    page_size = os.sysconf("SC_PAGESIZE") // ProcStatmIndex.BYTES_TO_KB
                    rss_pages = int(fields[ProcStatmIndex.RSS])
                    rss_kb = rss_pages * page_size
                except (ValueError, AttributeError):
                    pass
    except (FileNotFoundError, PermissionError):
        pass
    return rss_kb

def get_process_mem_percent(pid: int) -> float:
    """
    Returns memory usage percentage of a process.

    Parameters:
        pid (int): Process ID

    Returns:
        float: Memory usage percent (0.0 - 100.0)
    """
    rss = _read_proc_rss(pid)
    mem_total = _read_meminfo_total()

    if mem_total <= MemInfoIndex.MEM_INVALID:
        return MemInfoIndex.MEM_INVALID

    mem_percent = (rss / mem_total) * MemInfoIndex.MEM_PERCENT_SCALE
    return round(mem_percent, MemInfoIndex.MEM_PERCENT_ROUND_DIGITS)
