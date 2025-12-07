"""
user.py

Provides functions to retrieve the username of a process owner on a Linux system.

Shows:
- Converting numeric UID to username via /etc/passwd
- Retrieving the username owning a given process
- Handling missing processes or permission errors gracefully

Dependencies:
- Standard Python libraries: os
- backend.file_helpers for safely reading system files
- backend.process_constants for /etc/passwd field indices
"""

import os
from backend.process_constants import PasswdIndex
from backend.file_helpers import read_file


def _uid_to_username(uid: int) -> str | None:
    """
    Helper:
    Convert a numeric UID to a username using /etc/passwd.

    Args:
        uid (int): User ID to look up.

    Returns:
        str | None: Username if found, otherwise None.
    """

    username: str | None = None
    passwd_path = "/etc/passwd"

    data = read_file(passwd_path)
    if data is not None:
        for line in data.splitlines():
            parts = line.strip().split(":")
            if len(parts) <= PasswdIndex.UID:
                continue
            try:
                entry_uid = int(parts[PasswdIndex.UID])
            except ValueError:
                print(
                    f"Warning: Invalid UID in {passwd_path}: {parts[PasswdIndex.UID]}"
                )
                continue
            if entry_uid == uid:
                username = parts[PasswdIndex.NAME]
                break

    return username


def get_process_user(pid: int) -> str | None:
    """
    Retrieve the username that owns a specific process.

    Args:
        pid (int): Process ID.

    Returns:
        str | None: Username if found, otherwise None.
    """

    username: str | None = None
    proc_path = f"/proc/{pid}"

    try:
        # Get file status of the process directory to retrieve UID
        proc_stat = os.stat(proc_path)
        process_uid = proc_stat.st_uid

        # Convert UID to username
        username = _uid_to_username(process_uid)

    except FileNotFoundError:
        print(
            f"Error: Process directory {proc_path} not found. PID {pid} may not exist."
        )
    except PermissionError:
        print(
            f"Error: Permission denied accessing {proc_path}. Cannot determine owner of PID {pid}."
        )

    return username
