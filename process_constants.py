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
    STARTTIME = 21
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
    CPU_DEFAULT_COUNT = 1
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

    # Device major numbers
    MAJOR_VT = 4  # virtual console (tty1-tty6)
    MAJOR_PTS = 136  # pseudo-terminal (pts/N)

    # Bit masks and shifts for decoding tty_nr
    MAJOR_SHIFT = 8
    MAJOR_MASK = 0xFFF

    MINOR_LOW_MASK = 0xFF
    MINOR_HIGH_SHIFT = 12
    MINOR_HIGH_MASK = 0xFFF00


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
        "foreground": "+",  # Foreground
        # Add more flags here as needed
    }


class UptimeIndex:
    """
    Constants representing the indices of fields in /proc/uptime.
    """

    SYSTEM_UPTIME = 0
    IDLE_TIME = 1


class TimeFormatIndex:
    """
    Constants for formatting time values in ps-style columns.
    """

    DEFAULT_TIME = "0:00"
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_DAY = 86400
    HOURS_PER_DAY = 24
