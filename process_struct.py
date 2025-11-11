#!/usr/bin/python3
"""
process_struct.py

This module defines the ProcessInfo dataclass, which represents a system process
with attributes corresponding to the columns of `ps aux`:

    USER, PID, %CPU, %MEM, VSZ, RSS, TTY, STAT, START, TIME, COMMAND

It is intended for use in system monitoring tools and other process management
utilities.

Usage Example:
    from process_struct import ProcessInfo

    p = ProcessInfo(
        user="root",
        pid=1234,
        cpu_percent=0.1,
        mem_percent=0.5,
        vsz=1048576,
        rss=204800,
        tty="?",
        stat="S",
        start="12:34",
        time="00:01:23",
        command="/usr/bin/python3"
    )
"""

from dataclasses import dataclass

@dataclass
class ProcessInfo:
    """
    Dataclass representing a system process.

    Attributes:
        user (str): Owner of the process.
        pid (int): Process ID.
        cpu_percent (float): CPU usage percentage.
        mem_percent (float): Memory usage percentage.
        vsz (int): Virtual memory size in KB.
        rss (int): Resident memory size in KB.
        tty (str): Terminal associated with the process.
        stat (str): Process state (e.g., S, R, Z).
        start (str): Process start time (HH:MM).
        time (str): Total CPU time used (HH:MM:SS).
        command (str): Command that launched the process.
    """
    user: str
    pid: int
    cpu_percent: float
    mem_percent: float
    vsz: int
    rss: int
    tty: str
    stat: str
    start: str
    time: str
    command: str

    def __post_init__(self):
        if not (0 <= self.cpu_percent <= 100):
            raise ValueError(f"cpu_percent must be between 0 and 100, got {self.cpu_percent}")
        if not (0 <= self.mem_percent <= 100):
            raise ValueError(f"mem_percent must be between 0 and 100, got {self.mem_percent}")
        if self.pid < 0:
            raise ValueError(f"PID must be non-negative, got {self.pid}")
