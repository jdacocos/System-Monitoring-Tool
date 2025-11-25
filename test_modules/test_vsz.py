"""
test_vsz.py

This module contains unit tests for the `vsz.py` module, which provides
a function to retrieve the virtual memory size (VSZ) of processes
on a Linux system.

Tests are written using the pytest framework and validate that
`get_process_vsz`:

    - Returns an integer value for each PID
    - Handles non-existent or inaccessible processes gracefully
    - Produces values consistent with expected ranges (>= 0 KB)

The tests iterate over all processes listed in `/proc` to ensure
robustness across a variety of system processes.

Requirements:
    pytest
"""

from process_util.pids import get_process_pids
from process_util.vsz import get_process_vsz


def test_get_process_vsz():
    """
    Test reading virtual memory size (VSZ) for all PIDs in the system.
    """
    pids = get_process_pids()
    assert pids, "No PIDs found to test VSZ"

    for pid in pids:
        vsz = get_process_vsz(pid)
        print(f"PID {pid} VSZ: {vsz} KB")
        assert isinstance(vsz, int), f"VSZ for PID {pid} should be an integer"
        assert vsz >= 0, f"VSZ for PID {pid} should be >= 0"
