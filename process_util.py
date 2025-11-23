from process_struct import ProcessInfo
from process_constants import ProcessStateIndex, CpuStatIndex, PasswdIndex

import os
import time
from typing import Iterator

LNX_FS = '/proc'
CPU_LABEL_COLUMN = 1
CPU_PERCENT_SCALE = 100.0
CPU_PERCENT_ROUND_DIGITS = 2
CPU_PERCENT_INVALID = 0.0
MIN_DELTA_TOTAL = 0


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
                fields = line.split()[CPU_LABEL_COLUMN:]
                total_jiffies = sum(int(fields[i]) for i in range(CpuStatIndex.IDLE + 1)) # sum USER + NICE + SYSTEM + IDLE
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

    # Sleep for the interval
    time.sleep(interval)

    # Read jiffies again
    proc_jiffies_2 = _read_proc_pid_time(pid)
    total_jiffies_2 = _read_proc_stat_total()

    # Compute differences
    delta_proc = proc_jiffies_2 - proc_jiffies_1
    delta_total = total_jiffies_2 - total_jiffies_1

    # Avoid division by zero
    if delta_total <= MIN_DELTA_TOTAL:
        return CPU_PERCENT_INVALID

    cpu_percent = (delta_proc / delta_total) * CPU_PERCENT_SCALE
    return round(cpu_percent, CPU_PERCENT_ROUND_DIGITS)

