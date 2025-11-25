"""
test_mem_percent.py

This module contains unit tests for mem_percent.py, which provides
functions for calculating process memory usage as a percentage
of total system memory.

Tests are written using the pytest framework. Each test validates:

- That get_process_mem_percent(pid) returns a float.
- The returned memory percentage is within the expected range (0.0 - 100.0).
- The function behaves correctly for multiple processes, including
  edge cases like PIDs that may no longer exist or system processes.

Requirements:
    pytest
"""

import os
import pytest
from process_util.pids import get_process_pids
from process_util.mem_percent import get_process_mem_percent


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

    # --- Test 3: Loop over all PIDs from ps aux ---
    for pid in pids:
        mem = get_process_mem_percent(pid)
        print(f"PID {pid} Memory: {mem}%")
        assert isinstance(mem, float), f"Memory percent for PID {pid} should be a float"
        assert (
            0.0 <= mem <= 100.0
        ), f"Memory percent for PID {pid} should be between 0 and 100"
