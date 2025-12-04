"""
test_user.py

Unit tests for user.py module, which retrieves usernames of process owners
on a Linux system.

Tests verify:
    - UID to username mapping
    - Process owner retrieval for real PIDs
    - Comparison against psutil
    - Graceful handling of missing or inaccessible /proc entries

Requirements:
    pytest
    psutil (for comparison test)
Linux-only: Requires access to /proc and /etc/passwd.
"""

import os
import pytest
import psutil
from process_util.pids import get_process_pids
from process_util.user import _uid_to_username, get_process_user


def test_uid_to_username():
    """Test that current UID is correctly mapped to username."""
    uid = os.getuid()
    username = _uid_to_username(uid)
    print(f"Current UID {uid} corresponds to user: {username}")
    assert username is not None
    assert isinstance(username, str)
    assert len(username) > 0


def test_get_process_user_real_pids():
    """Test get_process_user returns valid usernames for real PIDs."""
    pids = get_process_pids()
    assert len(pids) > 0, "No processes found on system."

    for pid in pids:
        user = get_process_user(pid)
        # Process may disappear, skip if None
        if user is None:
            continue
        assert isinstance(user, str)
        assert len(user) > 0


@pytest.mark.skipif(not psutil, reason="psutil not installed")
def test_get_process_user_against_psutil():
    """
    Compare get_process_user() output with psutil.Process().username().
    Skips processes that raise AccessDenied or NoSuchProcess in psutil.
    """
    pids = get_process_pids()
    for pid in pids:
        try:
            ps_user = psutil.Process(pid).username()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        user = get_process_user(pid)
        if user is None:
            continue

        # On many Linux systems, psutil returns 'root' and our function may return same
        # For UID-based processes, they should match
        assert user == ps_user, f"Mismatch for PID {pid}: {user} != {ps_user}"
