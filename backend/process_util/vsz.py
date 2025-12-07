"""
vsz.py

Provides functions to retrieve the virtual memory size (VSZ) of a process
on a Linux system, corresponding to the VSZ column in `ps aux`.

Shows:
- Reading /proc/<pid>/stat to extract VSZ
- Converting VSZ from bytes to KB
- Graceful handling of missing processes or malformed data

Dependencies:
- Standard Python libraries: None
- backend.file_helpers for safe file reading
- backend.process_constants for field indices
"""

from backend.process_constants import ProcessStateIndex, ProcStatmIndex
from backend.file_helpers import read_file


def get_process_vsz(pid: int) -> int:
    """
    Retrieve the virtual memory size (VSZ) of a process in KB.

    Args:
        pid (int): Process ID.

    Returns:
        int: VSZ in KB, or 0 if the process cannot be read or the value is invalid.
    """

    vsz_kb = 0
    stat_content = read_file(f"/proc/{pid}/stat")

    if stat_content:
        fields = stat_content.split()
        if len(fields) > ProcessStateIndex.VSZ:
            try:
                vsz_bytes = int(fields[ProcessStateIndex.VSZ])
                vsz_kb = vsz_bytes // ProcStatmIndex.BYTES_TO_KB
            except ValueError as e:
                print(
                    f"[ERROR] Invalid VSZ value for PID "
                    f"{pid}: {fields[ProcessStateIndex.VSZ]} ({e})"
                )
        else:
            print(f"[WARN] Not enough fields in /proc/{pid}/stat to read VSZ")
    else:
        print(f"[WARN] Could not read /proc/{pid}/stat")

    return vsz_kb
