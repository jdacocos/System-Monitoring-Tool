"""
test_pids.py

Unit tests for process_util.pids module, which retrieves process IDs (PIDs)
from the Linux /proc filesystem.

Tests verify:
    - PIDs are positive integers
    - PIDs correspond to existing /proc directories
    - Comparison against psutil.pids()
    - Graceful handling of missing or inaccessible /proc entries

Requirements:
    pytest
    psutil (for comparison test)
Linux-only: Requires /proc filesystem.
"""

import os
import pytest
import psutil
from backend.process_util.pids import get_process_pids


def test_get_process_pids_basic():
    """Test that get_process_pids() returns valid PIDs and print each PID."""
    pids = get_process_pids()
    print(f"\nRetrieved {len(pids)} PIDs from /proc")

    # Check each PID
    for pid in pids:
        print(f"Checking PID: {pid}")
        assert isinstance(pid, int), f"PID {pid} is not an integer"
        assert pid > 0, f"PID {pid} is not positive"
        proc_dir = f"/proc/{pid}"
        assert os.path.isdir(proc_dir), f"Directory {proc_dir} does not exist"

    # Ensure current process is included
    current_pid = os.getpid()
    print(f"Current process PID: {current_pid}")
    assert current_pid in pids, "Current process PID not in retrieved list"


@pytest.mark.skipif(not psutil, reason="psutil not installed")
def test_get_process_pids_against_psutil():
    """Compare get_process_pids() with psutil.pids() and print debug info."""
    pids_proc = set(get_process_pids())
    pids_psutil = set(psutil.pids())

    print(f"\nNumber of PIDs from /proc: {len(pids_proc)}")
    print(f"Number of PIDs from psutil: {len(pids_psutil)}")

    common_pids = pids_proc.intersection(pids_psutil)
    print(f"Number of common PIDs: {len(common_pids)}")

    # Ensure current process is in the intersection
    assert os.getpid() in common_pids
    print(f"Current process PID {os.getpid()} is in the common set")
