"""
test_vsz.py

Unit tests for vsz.py, which retrieves the virtual memory size (VSZ)
of processes on a Linux system.

Tests are written using pytest and validate that get_process_vsz:

    - Returns an integer value for each PID
    - Handles non-existent or inaccessible processes gracefully
    - Produces values consistent with expected ranges (>= 0 KB)
    - Matches psutil's reported virtual memory size (VSZ) for rigorous checking
"""

import psutil
from backend.process_util.pids import get_process_pids
from backend.process_util.vsz import get_process_vsz


def test_get_process_vsz():
    """
    Test reading virtual memory size (VSZ) for all PIDs in the system
    and compare against psutil.
    """
    pids = get_process_pids()
    assert pids, "No PIDs found to test VSZ"

    print(f"Comparing VSZ for {len(pids)} PIDs with psutil...")

    for pid in pids:
        vsz = get_process_vsz(pid)
        print(f"PID {pid} VSZ: {vsz} KB")

        # Basic type and range checks
        assert isinstance(vsz, int), f"VSZ for PID {pid} should be an integer"
        assert vsz >= 0, f"VSZ for PID {pid} should be >= 0"

        # Compare with psutil if available
        try:
            p = psutil.Process(pid)
            psutil_vsz = p.memory_info().vms // 1024  # Convert bytes to KB
            print(f"PID {pid} psutil VSZ: {psutil_vsz} KB")
            # Allow some tolerance, e.g., 1-2 KB, due to timing differences
            assert abs(vsz - psutil_vsz) <= 2, f"PID {pid} VSZ mismatch with psutil"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Skip PIDs that have exited or are inaccessible
            print(
                f"PID {pid} skipped for psutil comparison (NoSuchProcess/AccessDenied)"
            )
