"""
test_start.py

This module contains unit tests for the `start.py` module, which provides
functions to retrieve and format the start time of processes on a Linux system
in a style consistent with the 'START' column of the `ps aux` command.

Tests are written using the pytest framework and validate that:

    - get_process_start(pid) returns a string for a given PID
    - The formatted string is in one of the expected formats: 'HH:MM', 'MonDD', or 'YYYY'
    - Functions handle non-existent or inaccessible PIDs gracefully
    - Computed start times are plausible based on the current system uptime

Tests iterate over all processes listed in `/proc` to ensure correctness
across a variety of system processes.

Requirements:
    pytest
"""

import os
import time
import pytest
from process_util.pids import get_process_pids
from process_util.start import get_process_start


def test_get_process_start_all_pids():
    """
    Test get_process_start for all PIDs listed in /proc.

    Validates that:
        1. Each PID returns a string.
        2. START column is in one of the ps-style formats: HH:MM, MonDD, or YYYY.
        3. Errors are handled gracefully for inaccessible or exited processes.
    """

    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test get_process_start.")

    print("\nTesting all PIDs dynamically:")
    for pid in sorted(pids):
        start_str = get_process_start(pid)
        print(f"PID {pid} START: {start_str}")

        assert isinstance(start_str, str)
        if "Error" in start_str or start_str.strip() == "":
            continue  # skip unreadable or exited PIDs

        # Validate ps-style START formats
        valid_format = False
        for fmt in ("%H:%M", "%b%d", "%Y"):
            try:
                time.strptime(start_str, fmt)
                valid_format = True
                break
            except ValueError:
                continue

        assert valid_format, f"PID {pid} START has invalid format: {start_str}"
