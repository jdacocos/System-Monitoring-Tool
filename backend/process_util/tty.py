"""
tty.py

Provides functions to retrieve the terminal (TTY) associated with a process
on a Linux system.

Shows:
- Converting numeric tty_nr from /proc/<pid>/stat to human-readable TTY names
- Retrieving the TTY name for a given process
- Returning a default TTY name if the process has no associated terminal

Dependencies:
- backend.process_constants for TTY constants and mappings
- backend.file_helpers for safely reading /proc files
"""

from backend.process_constants import ProcessStateIndex, TTYMapIndex
from backend.file_helpers import read_file


def read_tty_nr_to_name(tty_nr: int) -> str:
    """
    Convert numeric tty_nr to a human-readable TTY name.

    Args:
        tty_nr (int): TTY number from /proc/<pid>/stat

    Returns:
        str: TTY name (e.g., 'pts/0', 'tty1') or DEFAULT_TTY if invalid or unrecognized.
    """

    if tty_nr <= 0:
        return TTYMapIndex.DEFAULT_TTY

    major = (tty_nr >> TTYMapIndex.MAJOR_SHIFT) & TTYMapIndex.MAJOR_MASK
    minor = (tty_nr & TTYMapIndex.MINOR_LOW_MASK) | (
        (tty_nr >> TTYMapIndex.MINOR_HIGH_SHIFT) & TTYMapIndex.MINOR_HIGH_MASK
    )

    if major == TTYMapIndex.MAJOR_VT:
        return f"tty{minor}"
    if major == TTYMapIndex.MAJOR_PTS:
        return f"pts/{minor}"

    return TTYMapIndex.DEFAULT_TTY


def get_process_tty(pid: int) -> str:
    """
    Retrieve the human-readable TTY name for a given process.

    Args:
        pid (int): Process ID

    Returns:
        str: TTY name (e.g., 'pts/0', 'tty1') or DEFAULT_TTY if unavailable.
    """

    tty_name = TTYMapIndex.DEFAULT_TTY
    stat_path = f"/proc/{pid}/stat"

    stat_content: str | None = read_file(stat_path)

    if stat_content:
        fields = stat_content.split()
        if len(fields) > ProcessStateIndex.TTY_NR:
            try:
                tty_nr = int(fields[ProcessStateIndex.TTY_NR])
                tty_name = read_tty_nr_to_name(tty_nr)
            except ValueError:
                print(
                    f"[WARN] Invalid TTY_NR value for PID {pid}: {fields[ProcessStateIndex.TTY_NR]}"
                )
        else:
            print(f"[WARN] Not enough fields in {stat_path} to read TTY_NR")
    else:
        print(f"[WARN] Could not read {stat_path}")

    return tty_name
