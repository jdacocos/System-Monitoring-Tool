"""
test_process_util.py

This module contains unit tests for the process_util.py module, 
which provides functions for retrieving process information 
on a Linux system, including CPU and memory usage percentages, 
user ownership, and PID listing.

Tests are written using the pytest framework. Each test validates
that the functions return correct types, expected value ranges, 
and handle edge cases gracefully.

Requirements:
    pytest
"""
import os
import pytest
from process_struct import ProcessInfo
from process_util import (
    open_file_system, get_process_pids, get_process_user,
    get_process_cpu_percent, get_process_mem_percent, get_process_vsz,
    get_process_rss,
    _uid_to_username, _read_proc_stat_total, _read_proc_pid_time,
    _read_meminfo_total
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

def test_get_process_cpu_percent():
    """
    Test get_process_cpu_percent() with:
      1. Busy PID (current Python process)
      2. First PID (usually idle PID 1)
      3. A few PIDs to check type and range
    """

    pids = get_process_pids()
    print(f"Found PIDs: {pids[:10]}...")  # only print first 10

    # --- Test 1: Busy PID ---
    busy_pid = os.getpid()  # PID of this Python process
    cpu_busy = get_process_cpu_percent(busy_pid, interval=0.5)
    print(f"CPU percent for busy PID {busy_pid}: {cpu_busy}%")
    assert isinstance(cpu_busy, float), "CPU percent should be a float"
    assert 0.0 <= cpu_busy <= 100.0, "CPU percent should be between 0 and 100"

    # --- Test 2: First PID (likely idle) ---
    first_pid = pids[0] if pids else 1
    cpu_first = get_process_cpu_percent(first_pid, interval=0.5)
    print(f"CPU percent for first PID {first_pid}: {cpu_first}%")
    assert isinstance(cpu_first, float), "CPU percent should be a float"
    assert 0.0 <= cpu_first <= 100.0, "CPU percent should be between 0 and 100"

    # --- Test 3: Loop over a few PIDs ---
    for pid in pids[:5]:
        cpu = get_process_cpu_percent(pid, interval=0.5)
        print(f"PID {pid} CPU: {cpu}%")
        assert isinstance(cpu, float), f"CPU percent for PID {pid} should be a float"
        assert 0.0 <= cpu <= 100.0, f"CPU percent for PID {pid} should be between 0 and 100"

def test_read_meminfo_total():
    """Test reading total system memory from /proc/meminfo"""
    total_mem = _read_meminfo_total()
    print(f"Total system memory: {total_mem} KB")
    assert total_mem > 0  # should be positive on any system

def test_get_process_rss():
    """Test reading resident set size for a real process"""
    pids = get_process_pids()
    assert pids, "No PIDs found to test RSS"
    test_pid = pids[0]
    
    rss = get_process_rss(test_pid)
    print(f"RSS for PID {test_pid}: {rss} KB")
    assert rss >= 0  # should be 0 or positive

def test_get_process_mem_percent():
    """
    Test get_process_mem_percent() with:
      1. Busy PID (current Python process)
      2. First PID (usually idle PID 1)
      3. A few PIDs to check type and range
    """
    pids = get_process_pids()
    print(f"Found PIDs: {pids[:10]}...")  # only print first 10 to avoid flooding
    assert pids, "No PIDs found to test memory percent"

    # --- Test 1: Busy PID ---
    busy_pid = os.getpid()  # PID of this Python process
    mem_busy = get_process_mem_percent(busy_pid)
    print(f"Memory percent for busy PID {busy_pid}: {mem_busy}%")
    assert isinstance(mem_busy, float), "Memory percent should be a float"
    assert 0.0 <= mem_busy <= 100.0, "Memory percent should be between 0 and 100"

    # --- Test 2: First PID (likely idle) ---
    first_pid = pids[0] if pids else 1
    mem_first = get_process_mem_percent(first_pid)
    print(f"Memory percent for first PID {first_pid}: {mem_first}%")
    assert isinstance(mem_first, float), "Memory percent should be a float"
    assert 0.0 <= mem_first <= 100.0, "Memory percent should be between 0 and 100"

    # --- Test 3: Loop over a few PIDs ---
    for pid in pids[:5]:
        mem = get_process_mem_percent(pid)
        print(f"PID {pid} Memory: {mem}%")
        assert isinstance(mem, float), f"Memory percent for PID {pid} should be a float"
        assert 0.0 <= mem <= 100.0, f"Memory percent for PID {pid} should be between 0 and 100"
        
def test_get_process_vsz():
    """
    Test get_process_vsz() with:
      1. Busy PID (current Python process)
      2. First PID (usually PID 1)
      3. A few PIDs to check type and range
    """

    pids = get_process_pids()
    print(f"Found PIDs: {pids[:10]}...")  # Only print first 10 to avoid flooding

    # --- Test 1: Busy PID ---
    busy_pid = os.getpid()  # PID of this Python process
    vsz_busy = get_process_vsz(busy_pid)
    print(f"VSZ for busy PID {busy_pid}: {vsz_busy} KB")
    assert isinstance(vsz_busy, int), "VSZ should be an integer"
    assert vsz_busy >= 0, "VSZ must be non-negative"

    # --- Test 2: First PID (likely idle) ---
    first_pid = pids[0] if pids else 1
    vsz_first = get_process_vsz(first_pid)
    print(f"VSZ for first PID {first_pid}: {vsz_first} KB")
    assert isinstance(vsz_first, int), "VSZ should be an integer"
    assert vsz_first >= 0, "VSZ must be non-negative"

    # --- Test 3: Loop over a few PIDs ---
    for pid in pids[:5]:
        vsz = get_process_vsz(pid)
        print(f"PID {pid} VSZ: {vsz} KB")
        assert isinstance(vsz, int), f"VSZ for PID {pid} should be an integer"
        assert vsz >= 0, f"VSZ for PID {pid} must be non-negative"
