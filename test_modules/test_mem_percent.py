"""
test_mem_percent.py

Unit tests for mem_percent.py, which calculates process memory usage
as a percentage of total system memory.

Tests are written using the pytest framework. Each test validates:

- That get_process_mem_percent(pid) returns a float.
- Returned memory percentage is within the expected range (0.0 - 100.0).
- Comparison with psutil for rigorous validation.
- Handles multiple PIDs and edge cases gracefully.

Requirements:
    pytest
    psutil
Linux-only: Requires access to /proc filesystem.
"""

import os
import psutil
import pytest
from process_util.pids import get_process_pids
from process_util.mem_percent import get_process_mem_percent


def test_get_process_mem_percent_basic():
    """Test get_process_mem_percent for busy PID and first PID."""
    pids = get_process_pids()
    assert pids, "No PIDs found to test memory percent"

    # Busy PID (current Python process)
    busy_pid = os.getpid()
    mem_busy = get_process_mem_percent(busy_pid)
    print(f"Memory percent for busy PID {busy_pid}: {mem_busy}%")
    assert isinstance(mem_busy, float)
    assert 0.0 <= mem_busy <= 100.0

    # First PID (likely idle)
    first_pid = pids[0]
    mem_first = get_process_mem_percent(first_pid)
    print(f"Memory percent for first PID {first_pid}: {mem_first}%")
    assert isinstance(mem_first, float)
    assert 0.0 <= mem_first <= 100.0


def test_get_process_mem_percent_all_pids_psutil():
    """
    Test get_process_mem_percent against psutil for all PIDs.
    Prints all comparisons and asserts that values are within reasonable limits.
    """
    pids = get_process_pids()
    assert pids, "No PIDs found to test memory percent"

    total_mem_bytes = psutil.virtual_memory().total

    for pid in pids:
        try:
            proc = psutil.Process(pid)
            rss_bytes = proc.memory_info().rss
            ps_mem_percent = (rss_bytes / total_mem_bytes) * 100
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            ps_mem_percent = None

        mem_percent = get_process_mem_percent(pid)
        print(f"PID {pid}: my_mem={mem_percent}%, psutil_mem={ps_mem_percent}%")

        # Only assert when psutil value exists
        if ps_mem_percent is not None:
            assert isinstance(mem_percent, float)
            assert 0.0 <= mem_percent <= 100.0
            # allow small differences due to rounding and sampling
            assert abs(mem_percent - ps_mem_percent) <= 2.0, (
                f"PID {pid} memory percent differs from psutil: "
                f"{mem_percent}% vs {ps_mem_percent}%"
            )
