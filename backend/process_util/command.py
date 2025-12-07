"""
command.py

Provides functions to retrieve the full command line of a process
on a Linux system, corresponding to the COMMAND column in `ps aux`.

Shows:
- Safe reading of /proc/<pid>/cmdline and /proc/<pid>/comm
- Fallback handling for kernel threads, zombies, and missing PIDs
- Normalization of null-separated command lines into space-separated strings

Integrates with backend file helpers and process stat utilities to:
- Retrieve command lines in a consistent format
- Handle inaccessible or special-state processes gracefully
"""

from backend.process_util.stat import read_process_stat_fields, base_state
from backend.file_helpers import read_file


def _read_cmdline(pid: int) -> str:
    """
    Helper:
    Reads /proc/<pid>/cmdline and converts null bytes to spaces.

    Args:
        pid (int): Process ID.

    Returns:
        str: Space-separated command line string, or empty string if unavailable.
    """

    cmdline_path = f"/proc/{pid}/cmdline"
    content = read_file(cmdline_path)
    return content.replace("\x00", " ").strip() if content else ""


def _read_comm(pid: int) -> str:
    """
    Helper:
    Reads /proc/<pid>/comm to retrieve the process name.

    Args:
        pid (int): Process ID.

    Returns:
        str: Process name, or "unknown" if the file cannot be read.
    """

    comm_path = f"/proc/{pid}/comm"
    content = read_file(comm_path)
    return content.strip() if content else "unknown"


def get_process_command(pid: int) -> str:
    """
    Returns the full command line of a process for the COMMAND column in ps aux.

    Fallback order:
        1. /proc/<pid>/cmdline
        2. /proc/<pid>/comm (for kernel threads)
        3. [zombie] for zombie processes
        4. [unknown] if all else fails

    Args:
        pid (int): Process ID.

    Returns:
        str: The command line or a descriptive fallback string
             such as "[zombie]", "[unknown]", "[kernel <pid>]",
             "[PID not found]", "[Permission denied]", or "[error]".
    """

    result = "[unknown]"
    try:
        # 1. Try full command line first
        cmd = _read_cmdline(pid)
        if cmd:
            result = cmd
        else:
            # 2. Read process stat for state
            fields = read_process_stat_fields(pid)
            state = base_state(fields) if fields else "?"

            # 3. Handle zombie processes
            if state == "Z":
                result = "[zombie]"
            # 4. Handle kernel threads and other special states
            elif state in {"I", "K", "R", "S", "D", "T", "t", "X", "x", "W"}:
                comm_name = _read_comm(pid)
                result = (
                    f"[{comm_name}]" if comm_name != "unknown" else f"[kernel {pid}]"
                )
            # 5. Else keep default "[unknown]"

    except FileNotFoundError:
        result = "[PID not found]"
    except PermissionError:
        result = "[Permission denied]"
    except OSError:
        result = "[error]"

    return result
