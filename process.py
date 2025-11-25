"""
process.py

This module provides functions to collect process information on a Linux system
and populate a list of ProcessInfo objects representing all running processes.
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


def populate_process_list() -> List[ProcessInfo]:
    """
    Populate a list of ProcessInfo instances for all running processes.

    Returns:
        List[ProcessInfo]: A snapshot of all processes similar to `ps aux`.
    """
    process_list: List[ProcessInfo] = []

    for pid in get_process_pids():
        try:
            process_list.append(
                ProcessInfo(
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
            )
        except (OSError, ValueError):
            # Skip processes that are gone, inaccessible, or fail to read
            continue

    return process_list
