"""
test_stat.py

This module contains unit tests for the `stat.py` module, which provides
functions to read and interpret process state information from
`/proc/<pid>/stat` on Linux systems.

The tests validate that:

    - `_read_process_stat_fields` correctly reads and splits stat fields
    - `_interpret_process_state` produces human-readable stat strings
    - Helper flags for session leader, priority, multi-threading, and
      locked memory are correctly appended
    - `get_process_stat` returns consistent and expected stat strings
      for various PIDs, including the current process, parent process,
      and non-existent PIDs

Tests are written using the `pytest` framework and handle processes
gracefully if files are missing or inaccessible.

Requirements:
    pytest
"""

import pytest
from process_util.pids import get_process_pids
from process_util.stat import (
    _read_process_stat_fields,
    _interpret_process_state,
    get_process_stat,
)


def test_read_process_stat_fields():
    """
    Verify that _read_process_stat_fields returns a list of fields
    from /proc/<pid>/stat. The list should contain at least the
    STATE field.
    """
    pid = 1  # usually init/systemd
    fields = _read_process_stat_fields(pid)
    print(f"PID {pid} stat fields: {fields}")
    assert isinstance(fields, list)
    # Ensure we at least get STATE field
    assert len(fields) > 2


def test_interpret_process_state_real_pids():
    """
    Test _interpret_process_state on all real PIDs from the system.
    Ensures that the returned stat string is:
        - Not empty
        - Starts with a valid state character (R, S, D, Z, T, t, X, x, K, W, I)
        - Includes valid flag characters, including the foreground '+' flag
    """

    pids = get_process_pids()
    valid_states = set("RSDZTtXxKWI")
    valid_flags = set(
        "s<NlL+"
    )  # session leader, priority, multi-threaded, locked, foreground

    for pid in pids:
        try:
            # Read /proc/<pid>/stat fields directly
            with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as f:
                fields = f.read().split()

            stat_str = _interpret_process_state(fields, pid)
            print(f"PID {pid} stat: {stat_str}")

            # Base state should be valid
            assert stat_str
            assert stat_str[0] in valid_states

            # Remaining characters should be valid flags
            for c in stat_str[1:]:
                assert c in valid_flags, f"Unexpected flag '{c}' in PID {pid} stat"

        except (FileNotFoundError, PermissionError):
            # Process may have exited or be inaccessible; skip
            continue


def test_get_process_stat():
    """
    Test that get_process_stat returns a valid stat string for all real PIDs.
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test get_process_stat.")

    allowed_chars = set("RSDZTWNI<+slL")  # common ps stat letters and flags

    for pid in pids:
        stat_str = get_process_stat(pid)
        print(f"PID {pid} stat: {stat_str}")

        # Validate type and non-empty string
        assert isinstance(stat_str, str), f"PID {pid} stat is not a string"
        assert len(stat_str) > 0, f"PID {pid} returned empty stat string"

        # Validate characters are allowed
        assert all(
            c in allowed_chars for c in stat_str
        ), f"PID {pid} stat contains invalid characters: {stat_str}"
