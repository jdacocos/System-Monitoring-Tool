"""
process_struct.py

Defines the ProcessInfo class representing a system process.

Shows:
- Mapping of process attributes to 'ps aux' columns
- Storage of CPU, memory, and other process metrics
- Validation of field values on initialization

Integrates with system monitoring tools and backend process utilities to:
- Represent process information consistently
- Enable population of process lists with typed data
- Support further analysis or display in dashboards
"""
from dataclasses import dataclass


# pylint: disable=too-many-instance-attributes


@dataclass(slots=True)
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
        nice (int): Nice value of the process.
        command (str): Full command that launched the process.
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
    nice: int
    command: str

    def __post_init__(self):
        """
        Validate process fields after initialization.

        Raises:
            ValueError: If PID is negative, or if cpu_percent or mem_percent are outside 0-100.
        """
        if self.pid < 0:
            raise ValueError(f"PID must be non-negative, got {self.pid}")

        if not 0 <= self.cpu_percent <= 100:
            raise ValueError(
                f"cpu_percent must be between 0 and 100, got {self.cpu_percent}"
            )

        if not 0 <= self.mem_percent <= 100:
            raise ValueError(
                f"mem_percent must be between 0 and 100, got {self.mem_percent}"
            )
