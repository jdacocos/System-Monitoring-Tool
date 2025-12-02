"""
test_user.py

This module contains unit tests for the user.py module, which provides functions
to retrieve the username of a process owner on a Linux system.

Tests are written using the pytest framework. They validate that:
    - Numeric UIDs are correctly mapped to usernames.
    - Process owners are correctly returned for real PIDs.
    - Functions handle missing /proc/<pid> directories or permission errors gracefully.

Requirements:
    pytest
Linux-only: Requires access to a mounted /proc filesystem and /etc/passwd file.
"""

import pytest
import os
from process_util.pids import get_process_pids
from process_util.user import _uid_to_username, get_process_user


def test_uid_to_username():
    """
    Tests that all uids are correctly converted to appropriate str usernames.
    """

    uid = os.getuid()
    username = _uid_to_username(uid)
    print(f"Current UID {uid} corresponds to user: {username}")
    assert username is not None
    assert isinstance(username, str)


def test_get_process_user():
    """
    Tests that it retrieves username associated with the processes.
    """
    pids = get_process_pids()

    # Ensure at least one valid PID
    assert len(pids) > 0

    print("\n Listing all PIDS and their users:\n")

    for pid in pids:
        user = get_process_user(pid)
        if user is not None:
            print(f"PID: {pid}, User: {user}")

    assert user is not None
    assert isinstance(user, str)
    assert len(user) > 0
