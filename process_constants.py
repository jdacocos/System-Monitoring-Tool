"""
process_constants.py

This module defines constants for the System Monitoring Tool.

Includes:
- ProcessStateIndex: Index positions of fields in /proc/<pid>/stat
- PasswdIndex: Index positions of fields in /etc/passwd
- ProcStatIndex: Index positions for /proc/stat CPU fields

These constants help prevent magic numbers and improve code readability.
"""

# pylint: disable=too-few-public-methods


class ProcessStateIndex:
    """
    Constants representing the indices of fields in /proc/<pid>/stat.
    The indices are 0-based.
    """

    PID = 0
    COMM = 1
    STATE = 2
    PPID = 3
    PGRP = 4
    SESSION = 5
    TTY_NR = 6
    TPGID = 7
    FLAGS = 8
    MINFLT = 9
    CMINFLT = 10
    MAJFLT = 11
    CMAJFLT = 12
    UTIME = 13
    STIME = 14
    # add more fields as needed
    NICE = 18
    NLWP = 19
    VSZ = 22
    LOCKED = 36


class CpuStatIndex:
    """
    Constants representing the indices of CPU fields in /proc/stat.
    These are used to calculate total CPU jiffies for the system.
    """

    USER = 0
    NICE = 1
    SYSTEM = 2
    IDLE = 3
    IOWAIT = 4
    IRQ = 5
    SOFTIRQ = 6
    STEAL = 7
    GUEST = 8
    GUEST_NICE = 9
    # constants for calculating cpu_percent
    CPU_LABEL_COLUMN = 1
    CPU_PERCENT_SCALE = 100.0
    CPU_PERCENT_ROUND_DIGITS = 2
    CPU_PERCENT_INVALID = 0.0
    MIN_DELTA_TOTAL = 0


class PasswdIndex:
    """
    Constants representing the 0-based indices of fields in /etc/passwd.
    """

    NAME = 0
    PASSWORD = 1
    UID = 2
    GID = 3
    COMMENT = 4
    HOME = 5
    SHELL = 6


class MemInfoIndex:
    """
    Constants representing the 0-based indices of fields in /proc/meminfo.
    """

    MEMTOTAL_LABEL = "MemTotal:"
    MEMTOTAL_VALUE = 1
    # constants for calculating mem_percent
    MEM_PERCENT_SCALE = 100.0
    MEM_PERCENT_ROUND_DIGITS = 2
    MEM_INVALID = 0.0


class ProcStatmIndex:
    """
    Constants representing the 0-based indices of fields in /proc/<pid>/statm
    """

    RSS = 1
    BYTES_TO_KB = 1024


class TTYMapIndex:
    """
    Mapping for numeric tty_nr values to readable TTY names.
    """

    DEFAULT_TTY = "?"

    # Common mappings (add more as needed)
    MAP = {
        34816: "pts/0",  # typical bash terminal
        34817: "pts/1",
        0x3: "tty1",
        0x4: "tty2",
        0x5: "tty3",
        0x6: "tty4",
        0x7: "tty5",
        0x8: "tty6",
    }


class StatMapIndex:
    """
    Maps numeric flags and kernel process states from /proc/<pid>/stat
    to the extended process state strings as seen in 'ps aux'.
    """

    DEFAULT_STAT = "?"
    DEFAULT_PRIORITY = 0
    MULTHREAD_THRESH = 1
    LOCKED_THRESH = 0

    # Main process states (kernel codes)
    STATE_MAP = {
        "R": "R",  # Running
        "S": "S",  # Sleeping
        "D": "D",  # Uninterruptible sleep
        "Z": "Z",  # Zombie
        "T": "T",  # Stopped
        "t": "t",  # Tracing stop
        "X": "X",  # Dead
        "x": "x",  # Dead (should not appear normally)
        "K": "K",  # Wakekill
        "W": "W",  # Waking
        "I": "I",  # Idle kernel thread
    }

    # Additional flag-based extensions
    FLAG_MAP = {
        "session_leader": "s",  # Process is session leader
        "high_priority": "<",  # High priority
        "low_priority": "N",  # Low priority
        "locked": "L",  # Pages locked in memory
        "multi_threaded": "l",  # Multi-threaded
        # Add more flags here as needed
    }
