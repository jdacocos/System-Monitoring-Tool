"""
process_struct.py

This module defines the ProcessInfo class, which represents a system process
with attributes corresponding to the columns of 'ps aux':

    USER, PID, %CPU, %MEM, VSZ, RSS, TTY, STAT, START, TIME, COMMAND

ProcessInfo instances store parsed data for use in system monitoring tools
and other process management components.
"""


# pylint: disable=too-many-instance-attributes
class ProcessInfo:
    """
    Class representing a system process.

    Attributes:
        user (str): USER column from ps aux.
        pid (int): PID column.
        cpu_percent (float): %CPU column.
        mem_percent (float): %MEM column.
        vsz (int): Virtual memory size in KB.
        rss (int): Resident memory size in KB.
        tty (str): Terminal associated with the process.
        stat (str): Process state flags.
        start (str): Process start time (format varies by uptime).
        time (str): Total CPU time ([[dd-]hh:]mm:ss).
        command (str): Full command that launched the process.
    """

    def __init__(
        self,
        user: str,
        pid: int,
        cpu_percent: float,
        mem_percent: float,
        vsz: int,
        rss: int,
        tty: str,
        stat: str,
        start: str,
        time: str,
        command: str,
    ):
        self.user = user
        self.pid = pid
        self.cpu_percent = cpu_percent
        self.mem_percent = mem_percent
        self.vsz = vsz
        self.rss = rss
        self.tty = tty
        self.stat = stat
        self.start = start
        self.time = time
        self.command = command

        self._validate()

    def _validate(self):
        """Validate input fields to prevent invalid process entries."""
        if self.pid < 0:
            raise ValueError(f"PID must be non-negative, got {self.pid}")

        if not (0 <= self.cpu_percent <= 100):
            raise ValueError(
                f"cpu_percent must be between 0 and 100, got {self.cpu_percent}"
            )

        if not (0 <= self.mem_percent <= 100):
            raise ValueError(
                f"mem_percent must be between 0 and 100, got {self.mem_percent}"
            )

    def __repr__(self):
        return (
            f"ProcessInfo(user={self.user!r}, pid={self.pid}, "
            f"cpu_percent={self.cpu_percent}, mem_percent={self.mem_percent}, "
            f"vsz={self.vsz}, rss={self.rss}, tty={self.tty!r}, stat={self.stat!r}, "
            f"start={self.start!r}, time={self.time!r}, command={self.command!r})"
        )
