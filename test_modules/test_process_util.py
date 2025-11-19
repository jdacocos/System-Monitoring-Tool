import pytest
import os

from process_struct import ProcessInfo
from process_util import (
    open_file_system, get_process_pids, get_process_user,
    _uid_to_username, _read_proc_stat_total, _read_proc_pid_time
    )

def test_open_file_system():
    """
    Tests that /proc path for the Linux file system correctly displays all contents.
    """

    fs = open_file_system()

    # 1. Ensure return type is ScandirIterator
    assert type(fs) is type(os.scandir("/"))

    # 2. Ensure iterating works (no errors)
    entries = list(fs)
    assert len(entries) > 0  # 3. /proc must contain something

    # Optional: ensure entries have names
    assert all(hasattr(e, "name") for e in entries)

    print(f"\n Print all contents of /proc:\n")
    for fs in entries:
        print(fs.name)
    
def test_get_process_pids():
    """
    Tests that all the pids are successfully retrieved from /proc.
    """

    pids = get_process_pids()

    # 1. Should return a list
    assert isinstance(pids, list)

    # 2. All entries should be integers
    assert all(isinstance(pid, int) for pid in pids)

    # 3. All PIDs should correspond to directories in /proc
    assert all(os.path.isdir(f"/proc/{pid}") for pid in pids)

    # 4. Process should be included
    current_pid = os.getpid()
    assert current_pid in pids

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

def test_read_proc_stat_total():
    """
    Tests that it returns the CPU jiffies.
    """
    total = _read_proc_stat_total()
    print(f"Total CPU jiffies: {total}")
    assert isinstance(total, int)
    assert total >= 0


def test_read_proc_pid_time():
    """
    Tests that it retrieves pid time.
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found")

    pid = pids[0]
    jiffies = _read_proc_pid_time(pid)
    print(f"PID {pid} total jiffies: {jiffies}")
    assert isinstance(jiffies, int)
    assert jiffies >= 0
