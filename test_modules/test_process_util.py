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
from process_util import (
    open_file_system,
    get_process_pids,
    get_process_user,
    get_process_cpu_percent,
    get_process_mem_percent,
    get_process_vsz,
    get_process_rss,
    get_process_tty,
    get_process_stat,
    _uid_to_username,
    _read_proc_stat_total,
    _read_proc_pid_time,
    _read_meminfo_total,
    _read_tty_nr_to_name,
    _read_process_stat_fields,
    _interpret_process_state,
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

    print("\nAll contents of /proc:")
    entries = open_file_system()
    for entry in entries:
        print(entry.name)


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
        assert (
            0.0 <= cpu <= 100.0
        ), f"CPU percent for PID {pid} should be between 0 and 100"


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
        assert (
            0.0 <= mem <= 100.0
        ), f"Memory percent for PID {pid} should be between 0 and 100"


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


def test_read_tty_nr_to_name():
    """
    Test the helper function _read_tty_nr_to_name().
    Checks for invalid and zero TTY numbers and ensures the return type is string.
    """
    # Invalid TTY number
    invalid_tty_nr = -1
    tty_name = _read_tty_nr_to_name(invalid_tty_nr)
    print(f"TTY name for invalid TTY nr {invalid_tty_nr}: {tty_name}")
    assert tty_name == "?", "Should return '?' for invalid TTY numbers"

    # Zero TTY number
    zero_tty_nr = 0
    tty_name = _read_tty_nr_to_name(zero_tty_nr)
    print(f"TTY name for zero TTY nr {zero_tty_nr}: {tty_name}")
    assert tty_name == "?", "Should return '?' for TTY number 0"


def test_get_process_tty():
    """
    Test get_process_tty() for deterministic TTYs.
    """

    # Test 1: Current Python process TTY
    current_pid = os.getpid()
    tty_current = get_process_tty(current_pid)
    print(f"Current PID {current_pid}: TTY = {tty_current}")
    assert isinstance(tty_current, str)
    assert tty_current != ""

    # Test 2: Parent shell process
    parent_pid = os.getppid()
    tty_parent = get_process_tty(parent_pid)
    print(f"Parent PID {parent_pid}: TTY = {tty_parent}")
    assert isinstance(tty_parent, str)
    assert tty_parent != ""

    # Test 3: Invalid PID
    invalid_tty = get_process_tty(999999)
    print(f"Invalid PID 999999: TTY = {invalid_tty}")
    assert invalid_tty == "?"

    # Test 4: PID 32335 (-bash)
    bash_pid = 32335
    tty = get_process_tty(bash_pid)
    print(f"PID {bash_pid}: TTY = {tty}")

    assert isinstance(tty, str), "TTY should be a string"
    assert tty == "pts/0", f"Expected 'pts/0' for PID {bash_pid}, got '{tty}'"


def test_read_process_stat_fields():
    """
    Verify that _read_process_stat_fields returns a list of fields
    from /proc/<pid>/stat. The list should contain at least the
    STATE field.
    """
    pid = 1  # usually init/systemd
    fields = _read_process_stat_fields(pid)
    print(f"PID {pid} stat fields: {fields}")
    assert isinstance(fields, list)
    # Ensure we at least get STATE field
    assert len(fields) > 2


def test_interpret_process_state_real_pids():
    """
    Test _interpret_process_state on a few real PIDs from the system.
    Ensures that the returned stat string is not empty and starts with
    a valid state character (R, S, D, Z, T, t, X, x, K, W, I).
    """

    # Pick first few PIDs from /proc
    pids = get_process_pids()[:5]
    valid_states = set("RSDZTtXxKWI")

    for pid in pids:
        try:
            # Read /proc/<pid>/stat fields directly
            with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as f:
                fields = f.read().split()

            stat_str = _interpret_process_state(fields, pid)
            print(f"PID {pid} stat: {stat_str}")

            # Base state should be valid
            assert stat_str
            assert stat_str[0] in valid_states

            # Stat string length should be at least 1
            assert len(stat_str) >= 1

        except (FileNotFoundError, PermissionError):
            # Process may have exited or be inaccessible; skip
            continue


def test_get_process_stat():
    """
    Test that get_process_stat returns a valid stat string for real PIDs.
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test get_process_stat.")

    for pid in pids[:20]:  # test first 10 PIDs
        stat_str = get_process_stat(pid)
        print(f"PID {pid} stat: {stat_str}")

        # Validate the type and non-empty
        assert isinstance(stat_str, str)
        assert len(stat_str) > 0

        # Optionally, check allowed characters: letters + typical ps flags
        allowed_chars = set("RSDZTWNI<+s")  # common ps stat letters and flags
        assert all(c in allowed_chars for c in stat_str)
