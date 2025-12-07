"""
test_nice.py

Unit tests for nice.py, which retrieves the NI (nice) value from /proc/<pid>/stat.

Tests now compare the results with psutil where applicable and
prints debug information for pytest -s.
"""

import pytest
import psutil
from backend.process_util.pids import get_process_pids
from backend.process_util.nice import get_process_nice


def test_get_process_nice_all_pids():
    """
    Test get_process_nice() for all PIDs in /proc.
    Validates that:
      - Each PID returns an integer
      - The nice value matches psutil where accessible
      - Kernel threads or inaccessible PIDs return 0
    Prints results for pytest -s.
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found to test nice values.")

    for pid in pids:
        nice_val = get_process_nice(pid)

        # Print basic info
        print(f"Testing PID {pid}: nice = {nice_val}")

        # Basic type check
        assert isinstance(nice_val, int), f"PID {pid} nice should be int"

        # Compare with psutil if accessible
        try:
            ps_proc = psutil.Process(pid)
            ps_nice = ps_proc.nice()  # returns int

            print(f"PID {pid}: psutil nice = {ps_nice}")
            if nice_val == ps_nice:
                print(f"PID {pid}: nice value matches psutil")
            else:
                print(f"PID {pid}: nice value mismatch")

            assert (
                nice_val == ps_nice
            ), f"PID {pid}: nice '{nice_val}' != psutil '{ps_nice}'"

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Expected for kernel threads or inaccessible processes
            print(f"PID {pid}: inaccessible, expected nice = 0")
            assert nice_val == 0, f"PID {pid}: expected 0 for inaccessible process"
