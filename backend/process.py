"""
process.py

Collects and returns information about all running processes on a Linux system.

Shows:
- Safe fetching of process data per PID
- CPU and memory percentage caching for efficiency
- Process attributes including user, PID, memory, CPU, TTY, status, and command

Integrates with the backend utilities to retrieve:
- User information
- CPU and memory usage
- Virtual memory and RSS
- TTY and status
- Start time and CPU time
- Nice value and command line
"""

from typing import List
from backend.process_struct import ProcessInfo
from backend.process_util.user import get_process_user
from backend.process_util.pids import get_process_pids
from backend.process_util.cpu_percent import get_process_cpu_percent
from backend.process_util.mem_percent import get_process_mem_percent
from backend.process_util.vsz import get_process_vsz
from backend.process_util.rss import get_process_rss
from backend.process_util.tty import get_process_tty
from backend.process_util.stat import get_process_stat
from backend.process_util.start import get_process_start
from backend.process_util.time import get_process_time
from backend.process_util.command import get_process_command
from backend.process_util.nice import get_process_nice


def _fetch_process(pid: int) -> ProcessInfo | None:
    """
    Helper:
    Safely fetches detailed information about a single process given its PID.

    Args:
        pid (int): The process ID to retrieve information for.

    Returns:
        ProcessInfo | None: A ProcessInfo object with the process details,
        or None if the process is inaccessible, exited, or invalid.
    """
    try:
        return ProcessInfo(
            user=get_process_user(pid),
            pid=pid,
            cpu_percent=get_process_cpu_percent(pid),
            mem_percent=get_process_mem_percent(pid),
            vsz=get_process_vsz(pid),
            rss=get_process_rss(pid),
            tty=get_process_tty(pid),
            stat=get_process_stat(pid),
            start=get_process_start(pid),
            time=get_process_time(pid),
            nice=get_process_nice(pid),
            command=get_process_command(pid),
        )
    except (OSError, ValueError):
        return None  # skip inaccessible processes


def populate_process_list() -> List[ProcessInfo]:
    """
    Populate a list of ProcessInfo objects for all running processes on the system.

    Returns:
        List[ProcessInfo]: A list containing ProcessInfo objects for each accessible process.
    """
    process_list: List[ProcessInfo] = []
    pids = get_process_pids()

    for pid in pids:
        proc_info = _fetch_process(pid)
        if proc_info is not None:
            process_list.append(proc_info)

    return process_list
