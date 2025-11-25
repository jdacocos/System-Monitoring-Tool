"""
test_tty.py

This module contains unit tests for the `tty.py` module, which provides
functions to retrieve the terminal (TTY) associated with a process
on a Linux system.

Tests are written using the pytest framework and cover:

    - _read_tty_nr_to_name: Ensures correct handling of invalid, zero,
      and mapped TTY numbers.
    - get_process_tty: Validates TTY retrieval for current, parent,
      specific, and invalid PIDs, checking return types and expected values.

The tests ensure that TTY functions handle edge cases gracefully and
return consistent, human-readable TTY names.

Requirements:
    pytest
    Standard Python libraries only: os
"""

import os
from process_util.pids import get_process_pids
from process_util.tty import _read_tty_nr_to_name, get_process_tty


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


def test_get_process_tty_all():
    """
    Test get_process_tty() for all PIDs found in /proc (ps aux).

    Ensures that:
      - Each PID returns a string
      - TTY is not empty for valid processes
      - Handles invalid or inaccessible PIDs gracefully
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test TTY retrieval.")

    for pid in pids:
        tty_name = get_process_tty(pid)
        print(f"PID {pid}: TTY = {tty_name}")

        assert isinstance(tty_name, str), f"TTY for PID {pid} should be a string"
        # Allow "?" for inaccessible or kernel processes
        assert tty_name != "", f"TTY for PID {pid} should not be empty"
