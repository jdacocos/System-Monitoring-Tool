"""
process.py

This module collects process information on a Linux system
and populates a list of ProcessInfo objects representing all running processes.

It uses cached CPU percentages to optimize performance in single-core environments.
"""

from typing import List
from process_struct import ProcessInfo
from process_util.user import get_process_user
from process_util.pids import get_process_pids
from process_util.cpu_percent import get_process_cpu_percent
from process_util.mem_percent import get_process_mem_percent
from process_util.vsz import get_process_vsz
from process_util.rss import get_process_rss
from process_util.tty import get_process_tty
from process_util.stat import get_process_stat
from process_util.start import get_process_start
from process_util.time import get_process_time
from process_util.command import get_process_command


def _fetch_process(pid: int) -> ProcessInfo | None:
    """
    Fetch a single PID's ProcessInfo safely.

    Returns None if the process is inaccessible, exited, or invalid.
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
            command=get_process_command(pid),
        )
    except (OSError, ValueError):
        return None  # skip inaccessible processes


def populate_process_list() -> List[ProcessInfo]:
    """
    Populate a list of ProcessInfo instances for all running processes.
    """
    process_list: List[ProcessInfo] = []
    pids = get_process_pids()

    for pid in pids:
        proc_info = _fetch_process(pid)
        if proc_info is not None:
            process_list.append(proc_info)

    return process_list
