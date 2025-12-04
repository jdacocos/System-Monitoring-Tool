"""
test_user.py

Unit tests for process_util.user module, which provides functions
to retrieve the username of a process owner on Linux.

Tests verify:
    - Numeric UIDs are correctly mapped to usernames
    - Process owners are correctly returned for real PIDs
    - Functions handle missing /proc/<pid> directories or permission errors gracefully
    - Prints all PIDs and corresponding usernames for runtime visibility

Requirements:
    pytest
Linux-only: Requires access to /proc filesystem and /etc/passwd
"""

import os
import pytest
import psutil
from process_util.pids import get_process_pids
from process_util.user import _uid_to_username, get_process_user


def test_uid_to_username():
    """Test that the current UID maps to a valid username."""
    uid = os.getuid()
    username = _uid_to_username(uid)
    print(f"\nCurrent UID {uid} corresponds to username: {username}")

    assert username is not None
    assert isinstance(username, str)
    assert len(username) > 0


def test_get_process_user_all_pids():
    """
    Test that get_process_user() retrieves usernames for all running PIDs.
    Prints all PIDs and their usernames.
    """
    pids = get_process_pids()
    print(f"\nRetrieved {len(pids)} PIDs from /proc")

    found_username = False

    for pid in pids:
        try:
            username = get_process_user(pid)
            print(f"PID: {pid}, User: {username}")
            if username is not None:
                found_username = True
                assert isinstance(username, str)
                assert len(username) > 0
        except Exception as e:
            # Fail gracefully if /proc/<pid> is inaccessible
            print(f"Warning: Could not retrieve user for PID {pid}: {e}")

    assert found_username, "No valid usernames were found for any PID"


@pytest.mark.skipif(not psutil, reason="psutil not installed")
def test_get_process_user_against_psutil():
    """
    Compare get_process_user() results with psutil.Process().username().
    Prints common PIDs and usernames.
    """
    pids = get_process_pids()
    common_found = False

    print("\nComparing with psutil usernames:")

    for pid in pids:
        try:
            my_user = get_process_user(pid)
            ps_user = psutil.Process(pid).username()
            print(f"PID: {pid}, file_helper user: {my_user}, psutil user: {ps_user}")

            # Only compare if both returned values
            if my_user and ps_user:
                common_found = True
                assert my_user == ps_user
        except (psutil.NoSuchProcess, PermissionError):
            continue  # Skip processes that no longer exist or are inaccessible

    assert common_found, "No PIDs had matching usernames between /proc and psutil"
