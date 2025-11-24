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
    # Add more fields as needed
    VSZ = 22

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
