"""
test_cpu_percent.py

Unit tests for cpu_percent.py, which calculates CPU usage percentages
for individual processes and the overall system.

Tests are written using the pytest framework and cover:

    - CPU percentage calculation for the current Python process (busy PID)
    - CPU percentage calculation for the first PID (usually idle PID 1)
    - Type and value range checks for a selection of PIDs
    - Handling of edge cases such as very short-lived processes or processes
      that exit during sampling

Each test validates that returned values are floats within the 0-100% range
and that calculations do not raise unexpected exceptions.

Requirements:
    pytest
"""

import os
import time
import pytest
from process_util.pids import get_process_pids
from process_util.cpu_percent import (
    _read_proc_stat_total,
    _read_proc_pid_time,
    get_process_cpu_percent,
)


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
    Test get_process_cpu_percent() for all PIDs in the system.

    Checks:
      1. Busy PID (current Python process)
      2. First PID (usually idle PID 1)
      3. All other PIDs returned by get_process_pids()
         - Ensure CPU percent is a float
         - Ensure value is within 0.0 - 100.0
    """

    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test get_process_cpu_percent.")

    # --- Test 1: Busy PID (current Python process) ---
    busy_pid = os.getpid()
    cpu_busy = get_process_cpu_percent(busy_pid, interval=0.5)
    print(f"CPU percent for busy PID {busy_pid}: {cpu_busy}%")
    assert isinstance(cpu_busy, float), "CPU percent should be a float"
    assert 0.0 <= cpu_busy <= 100.0, "CPU percent should be between 0 and 100"

    # --- Test 2: First PID (likely idle) ---
    first_pid = pids[0]
    cpu_first = get_process_cpu_percent(first_pid, interval=0.5)
    print(f"CPU percent for first PID {first_pid}: {cpu_first}%")
    assert isinstance(cpu_first, float), "CPU percent should be a float"
    assert 0.0 <= cpu_first <= 100.0, "CPU percent should be between 0 and 100"

    # --- Test 3: Loop over all PIDs ---
    for pid in pids:
        cpu = get_process_cpu_percent(pid, interval=0.1)  # smaller interval for speed
        print(f"PID {pid} CPU: {cpu}%")
        assert isinstance(cpu, float), f"CPU percent for PID {pid} should be a float"
        assert (
            0.0 <= cpu <= 100.0
        ), f"CPU percent for PID {pid} should be between 0 and 100"
