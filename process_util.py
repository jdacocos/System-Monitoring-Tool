from process_struct import ProcessInfo

import os
import pwd
import time
from typing import List

def _read_proc_stat(pid: int):

    """Return (comm, state) from /proc/<pid>/stat."""

    data = f.read().split()
    comm = data[1].strip("()")
    state = data[2]
    return comm, state

def _read_proc_status(pid: int):

    """Return (username, vsz, rss) from /proc/<pid>/status."""
    
    uid = None
    vsz = 0
    rss = 0
    with open(f"/proc/{pid}/status") as f:
        for line in f:
            if line.startswith("Uid:"):
                uid = int(line.split()[1])
            elif line.startswith("VmSize:"):
                vsz = int(line.split()[1])
            elif line.startswith("VmRSS:"):
                rss = int(line.split()[1])
    username = pwd.getpwuid(uid).pw_name if uid is not None else "unknown"
    return username, vsz, rss

def get_process_info(process_list: List[ProcessInfo], limit: int = 10) -> int:

    """
    Populate `process_list` with ProcessInfo objects from /proc.

    Returns:
        int: 0 if successfully retrieved processes, 1 if failed
    
    """
    fail = 0
    
    try:
        process_list.clear()

        for entry in os.listdir("/proc"):
            if not entry.isdigit():
                continue

            pid = int(entry)
            try:
                comm, state = _read_proc_stat(pid)
                username, vsz, rss = _read_proc_status(pid)

                # Placeholder CPU/mem and time
                cpu_percent = 0.0
                mem_percent = 0.0
                start = time.strftime("%H:%M")
                tty = "?"
                ttime = "00:00:00"

                process_list.append(ProcessInfo(
                    user=username,
                    pid=pid,
                    cpu_percent=cpu_percent,
                    mem_percent=mem_percent,
                    vsz=vsz,
                    rss=rss,
                    tty=tty,
                    stat=state,
                    start=start,
                    time=ttime,
                    command=comm
                ))
            except (PermissionError, FileNotFoundError):
                continue

            if len(process_list) >= limit:
                break

        return 0
    except Exception as e:
        print(f"Error retrieving process info: {e}")
        return 1
