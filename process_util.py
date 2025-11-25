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
    ProcessStateIndex,
    CpuStatIndex,
    PasswdIndex,
    MemInfoIndex,
    ProcStatmIndex,
    TTYMapIndex,
    StatMapIndex,
)

LNX_FS = "/proc"
RD_ONLY = "r"
UTF_8 = "utf-8"


def open_file_system(path=LNX_FS) -> Iterator[os.DirEntry]:
    """
    Open a directory iterator to the /proc file system.
    """

    entries = iter([])
    try:
        entries = os.scandir(path)
    except FileNotFoundError:
        print(f"Unable to open {path}")
    return entries


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
        with open(passwd_path, RD_ONLY, encoding=UTF_8) as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) <= PasswdIndex.UID:
                    continue
                try:
                    entry_uid = int(parts[PasswdIndex.UID])
                except ValueError:
                    print(
                        f"Warning: Invalid UID in {passwd_path}: {parts[PasswdIndex.UID]}"
                    )
                    continue
                if entry_uid == uid:
                    username = parts[PasswdIndex.NAME]
                    break
    except FileNotFoundError:
        print(f"Error: {passwd_path} not found. Cannot resolve UID {uid}.")
    except PermissionError:
        print(
            f"Error: Permission denied while reading {passwd_path}. "
            f"Cannot resolve UID {uid}."
        )
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
        print(
            f"Error: Process directory {proc_path} not found. PID {pid} may not exist."
        )
    except PermissionError:
        print(
            f"Error: Permission denied accessing {proc_path}. "
            f"Cannot determine owner of PID {pid}."
        )
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
        with open(stat_path, RD_ONLY, encoding=UTF_8) as f:
            first_line = f.readline()
            if first_line.startswith("cpu "):
                # skip the "cpu" label
                cpu_fields = first_line.split()[CpuStatIndex.CPU_LABEL_COLUMN :]

                # Sum USER + NICE + SYSTEM + IDLE (indexes defined in CpuStatIndex)
                total_jiffies = sum(
                    int(cpu_fields[i]) for i in range(CpuStatIndex.IDLE + 1)
                )

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
        with open(stat_path, RD_ONLY, encoding=UTF_8) as f:
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


def get_process_mem_percent(pid: int) -> float:
    """
    Calculate the memory usage percentage of a process.

    Parameters:
        pid (int): Process ID

    Returns:
        float: Memory usage percent (0.0 - 100.0)
    """
    rss_kb = get_process_rss(pid)
    total_mem_kb = _read_meminfo_total()

    # check division by zero or invalid total memory
    if total_mem_kb <= MemInfoIndex.MEM_INVALID:
        print(f"Warning: Total system memory invalid or unreadable for PID {pid}.")
        return float(MemInfoIndex.MEM_INVALID)

    mem_percent = (rss_kb / total_mem_kb) * MemInfoIndex.MEM_PERCENT_SCALE
    return round(mem_percent, MemInfoIndex.MEM_PERCENT_ROUND_DIGITS)


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


def _read_tty_nr_to_name(tty_nr: int) -> str:
    """
    Helper:
    Convert a numeric tty_nr value into a readable TTY name
    using the predefined TTY map.

    Parameters:
        tty_nr (int): TTY number from /proc/<pid>/stat

    Returns:
        str: TTY name (e.g., 'pts/0', 'tty1') or DEFAULT_TTY if not found
    """
    if tty_nr <= 0:
        return TTYMapIndex.DEFAULT_TTY

    return TTYMapIndex.MAP.get(tty_nr, TTYMapIndex.DEFAULT_TTY)


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


def _read_process_stat_fields(pid: int) -> list[str]:
    """
    Helper:
    Reads and splits the contents of /proc/<pid>/stat into fields.

    Parameters:
        pid (int): Process ID

    Returns:
        list[str]: List of fields from /proc/<pid>/stat, or empty list on error
    """
    stat_path = f"/proc/{pid}/stat"
    fields: list[str] = []
    try:
        with open(stat_path, RD_ONLY, encoding=UTF_8) as f:
            fields = f.read().split()
    except FileNotFoundError:
        print(f"[ERROR] Process {pid} stat file not found: {stat_path}")
    except PermissionError:
        print(f"[ERROR] Permission denied reading {stat_path}")
    except Exception as e:
        print(f"[ERROR] Unexpected error reading {stat_path}: {e}")
    return fields


def _interpret_process_state(fields: list[str], pid: int) -> str:
    """
    Helper:
    Converts /proc/<pid>/stat fields into a human-readable process stat string,
    combining the kernel state and any applicable flags such as session leader,
    priority, locked pages, or multi-threaded indicators.

    Parameters:
        fields (list[str]): Fields from /proc/<pid>/stat
        pid (int): Process ID

    Returns:
        str: Human-readable stat string (e.g., 'Ss<l') or DEFAULT_STAT
    """
    unknown_stat: str = StatMapIndex.DEFAULT_STAT
    if len(fields) <= ProcessStateIndex.STATE:
        print("[WARN] Not enough fields to read process state")
        return unknown_stat

    # Base kernel state
    stat_str = StatMapIndex.STATE_MAP.get(fields[ProcessStateIndex.STATE], unknown_stat)

    # Append session leader flag
    stat_str += _session_leader_flag(fields, pid)

    # Append high/low priority flags
    stat_str += _priority_flags(fields)

    # Append locked memory flag
    stat_str += _locked_flag(fields)

    # Append multi-threaded flag
    stat_str += _multi_threaded_flag(fields)

    return stat_str


def _base_state(fields: list[str]) -> str:
    """
    Return the main process state character (R, S, D, etc.).
    """
    return StatMapIndex.STATE_MAP.get(
        fields[ProcessStateIndex.STATE], StatMapIndex.DEFAULT_STAT
    )


def _session_leader_flag(fields: list[str], pid: int) -> str:
    """
    Return 's' if the process is a session leader.
    """
    try:
        return (
            StatMapIndex.FLAG_MAP["session_leader"]
            if int(fields[ProcessStateIndex.SESSION]) == pid
            else ""
        )
    except (ValueError, IndexError):
        return ""


def _priority_flags(fields: list[str]) -> str:
    """
    Return '<' or 'N' if process is high or low priority according to nice value.
    """
    flags_str = ""
    try:
        nice = int(fields[ProcessStateIndex.NICE])
        if nice < StatMapIndex.DEFAULT_PRIORITY:
            flags_str += StatMapIndex.FLAG_MAP["high_priority"]
        elif nice > StatMapIndex.DEFAULT_PRIORITY:
            flags_str += StatMapIndex.FLAG_MAP["low_priority"]
    except (ValueError, IndexError):
        pass
    return flags_str


def _multi_threaded_flag(fields: list[str]) -> str:
    """
    Return 'l' if the process has more than 1 thread.
    """

    try:
        nthreads = int(fields[ProcessStateIndex.NLWP])
        return (
            StatMapIndex.FLAG_MAP["multi_threaded"]
            if nthreads > StatMapIndex.MULTHREAD_THRESH
            else ""
        )
    except (ValueError, IndexError):
        return ""


def _locked_flag(fields: list[str]) -> str:
    """
    Return 'L' if the process has locked memory pages.
    """

    try:
        locked = int(fields[ProcessStateIndex.LOCKED])
        return (
            StatMapIndex.FLAG_MAP["locked"]
            if locked > StatMapIndex.LOCKED_THRESH
            else ""
        )
    except (ValueError, IndexError):
        return ""


def get_process_stat(pid: int) -> str:
    """
    Returns the human-readable process stat string for a given PID.

    Parameters:
        pid (int): Process ID

    Returns:
        str: Process stat string (e.g., 'Ss') or DEFAULT_STAT if unavailable
    """
    fields = _read_process_stat_fields(pid)
    return _interpret_process_state(fields, pid)
