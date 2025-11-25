"""
process_struct.py

This module defines the ProcessInfo dataclass, which represents a system process
with attributes corresponding to the columns of 'ps aux':

    USER, PID, %CPU, %MEM, VSZ, RSS, TTY, STAT, START, TIME, COMMAND

It is intended for use in system monitoring tools and other process management
utilities.
"""

from dataclasses import dataclass


@dataclass
# pylint: disable=too-many-instance-attributes
class ProcessInfo:
    """
    Dataclass representing a system process.

    Attributes:
        user (str): USER column in ps aux.
        pid (int): PID column in ps aux.
        cpu_percent (float): %CPU column in ps aux.
        mem_percent (float): %MEM column in ps aux.
        vsz (int): VSZ column in ps aux (virtual memory size in KB).
        rss (int): RSS column in ps aux (resident memory size in KB).
        tty (str): TTY column in ps aux (terminal associated with the process).
        stat (str): STAT column in ps aux (process state, e.g., S, R, Z).
        start (str): START column in ps aux (HH:MM, MonDD, or YYYY).
        time (str): TIME column in ps aux ([[dd-]hh:]mm:ss).
        command (str): COMMAND column in ps aux (command that launched the process).
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
        if not 0 <= self.cpu_percent <= 100:
            raise ValueError(
                f"cpu_percent must be between 0 and 100, got {self.cpu_percent}"
            )
        if not 0 <= self.mem_percent <= 100:
            raise ValueError(
                f"mem_percent must be between 0 and 100, got {self.mem_percent}"
            )
        if self.pid < 0:
            raise ValueError(f"PID must be non-negative, got {self.pid}")
