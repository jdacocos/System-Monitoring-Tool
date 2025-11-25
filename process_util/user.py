"""
user.py

This module provides functions for retrieving the username of a process owner
on a Linux system using the /proc filesystem and /etc/passwd file.

Functions:
    _uid_to_username(uid: int) -> str | None
        Helper function to convert a numeric UID to a username.
    get_process_user(pid: int) -> str | None
        Returns the username owning a specific process.

The module only uses standard libraries: os, typing.
"""

import os
from process_constants import RD_ONLY, UTF_8, PasswdIndex


def _uid_to_username(uid: int) -> str | None:
    """
    Helper: Convert a UID to a username using /etc/passwd.

    Parameters:
        uid (int): User ID to look up

    Returns:
        str | None: Username if found, otherwise None.
    """

    username = None
    passwd_path = "/etc/passwd"

    try:
        with open(passwd_path, RD_ONLY, encoding=UTF_8) as f:
            for line in f:
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
    except FileNotFoundError:
        print(f"Error: {passwd_path} not found. Cannot resolve UID {uid}.")
    except PermissionError:
        print(
            f"Error: Permission denied while reading {passwd_path}. "
            f"Cannot resolve UID {uid}."
        )
    return username


def get_process_user(pid: int) -> str | None:
    """
    Retrieve the username that owns a given process.

    Parameters:
        pid (int): Process ID

    Returns:
        str | None: Username if found, otherwise None.
    """

    proc_path = f"/proc/{pid}"
    username: str | None = None

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
            f"Error: Permission denied accessing {proc_path}. "
            f"Cannot determine owner of PID {pid}."
        )
    return username
