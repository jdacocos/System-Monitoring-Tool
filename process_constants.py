"""
process_constants.py

This module defines constants used for parsing the Linux /proc filesystem,
specifically for accessing fields in /proc/<pid>/stat and /proc/stat.
The constants are designed to prevent the use of “magic numbers” in code,
improving readability and maintainability.

The module includes:

- ProcessStateIndex: Contains indices for fields in /proc/<pid>/stat
  such as PID, COMM, STATE, UTIME, STIME, etc.

- CpuStatIndex: Contains indices for CPU fields in /proc/stat
  such as USER, NICE, SYSTEM, IDLE, etc.

Usage Example:
    from process_constants import ProcessStateIndex, CpuStatIndex

    # Access user and system CPU jiffies for a process
    utime_index = ProcessStateIndex.UTIME
    stime_index = ProcessStateIndex.STIME

    # Access total system CPU jiffies
    user_index = CpuStatIndex.USER
    system_index = CpuStatIndex.SYSTEM
"""

class ProcessStateIndex:
    """
    Constants representing the indices of fields in /proc/<pid>/stat.
    The indices are 0-based.

    Example fields:
        PID     - Process ID
        COMM    - Filename of the executable
        STATE   - Process state (R, S, Z, etc.)
        UTIME   - CPU time spent in user mode (jiffies)
        STIME   - CPU time spent in kernel mode (jiffies)
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


class CpuStatIndex:
    """
    Constants representing the indices of CPU fields in /proc/stat.
    These are used to calculate total CPU jiffies for the system.

    Example fields:
        USER    - Time spent in user mode
        NICE    - Time spent in user mode with low priority
        SYSTEM  - Time spent in system mode
        IDLE    - Time spent idle
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

class PasswdIndex:
    """
    Constants representing the 0-based indices of fields in /etc/passwd.

    Fields in each line of /etc/passwd are separated by ':':

        NAME     - Username (login name)
        PASSWORD - Password placeholder ('x' or encrypted, usually ignored)
        UID      - User ID
        GID      - Group ID
        COMMENT  - Optional comment or full name
        HOME     - Home directory
        SHELL    - Login shell
    """

    NAME = 0
    PASSWORD = 1
    UID = 2
    GID = 3
    COMMENT = 4
    HOME = 5
    SHELL = 6
