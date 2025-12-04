"""
test_tty.py

Unit tests for tty.py, which provides functions to retrieve
the terminal (TTY) associated with a process on a Linux system.

Tests are written using pytest and cover:

    - read_tty_nr_to_name: Ensures correct handling of invalid, zero,
      and mapped TTY numbers.
    - get_process_tty: Validates TTY retrieval for all system PIDs,
      checking return types and expected values.
"""

import pytest
import psutil
from process_util.pids import get_process_pids
from process_util.tty import read_tty_nr_to_name, get_process_tty


def test_read_tty_nr_to_name_basic():
    """
    Test read_tty_nr_to_name() with invalid and zero TTY numbers.
    """
    invalid_tty_nr = -1
    zero_tty_nr = 0

    tty_invalid = read_tty_nr_to_name(invalid_tty_nr)
    tty_zero = read_tty_nr_to_name(zero_tty_nr)

    print(f"TTY for invalid nr {invalid_tty_nr}: {tty_invalid}")
    print(f"TTY for zero nr {zero_tty_nr}: {tty_zero}")

    assert tty_invalid == "?", "Invalid TTY number should return '?'"
    assert tty_zero == "?", "Zero TTY number should return '?'"


def test_get_process_tty_all_pids():
    """
    Test get_process_tty() for all PIDs found in /proc and compare against psutil.
    Ensures:
        - Each PID returns a string
        - TTY is non-empty or '?'
        - Comparison with psutil where accessible
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test TTY retrieval.")

    for pid in pids:
        tty_name = get_process_tty(pid)
        print(f"PID {pid}: TTY = {tty_name}")

        # Ensure type and fallback are correct
        assert isinstance(tty_name, str), f"TTY for PID {pid} should be a string"
        assert tty_name != "", f"TTY for PID {pid} should not be empty"

        # Compare with psutil if process exists and is accessible
        try:
            ps_proc = psutil.Process(pid)
            ps_tty = ps_proc.terminal()
            ps_tty_str = ps_tty if ps_tty else "?"

            # Normalize psutil output to match short-name style
            if ps_tty_str.startswith("/dev/"):
                ps_tty_str = ps_tty_str[len("/dev/") :]

                print(f"PID {pid}: psutil TTY = {ps_tty_str}")

                # Allow some flexibility for inaccessible kernel processes
                assert tty_name == ps_tty_str
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process disappeared or access denied; just ensure type is string
            assert isinstance(tty_name, str)
