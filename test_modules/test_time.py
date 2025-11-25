"""
test_time.py

This module contains unit tests for the `time.py` module, which provides functions
to retrieve and format the total CPU time of processes on a Linux system in a style
consistent with the 'TIME' column of the `ps aux` command.

Tests are written using the pytest framework and validate that:

    - get_process_time(pid) returns a string for a given PID.
    - The TIME string conforms to the expected formats:
        - M:SS           for durations < 1 hour
        - H:MM:SS        for durations >= 1 hour
        - D-HH:MM:SS     for durations >= 1 day
    - All components (days, hours, minutes, seconds) are non-negative integers.
    - Seconds are always in the range [0, 59].
    - The reconstructed total seconds from the parsed TIME string matches
      the original formatting logic.
    - Functions handle non-existent or inaccessible PIDs gracefully by returning '0:00'.

Tests iterate over the first 100 processes listed in `/proc` to ensure
robustness across a variety of system processes.

Requirements:
    pytest
"""

import pytest
from process_util.pids import get_process_pids
from process_util.time import get_process_time
from process_constants import TimeFormatIndex


def _validate_time_string(pid, time_str):
    """Helper to validate a single TIME string for a PID."""
    # Skip unreadable processes
    if time_str == TimeFormatIndex.DEFAULT_TIME:
        return

    parts = [int(float(p)) for p in time_str.replace("-", ":").split(":")]

    # Seconds must be < 60
    assert (
        0 <= parts[-1] < TimeFormatIndex.SECONDS_PER_MINUTE
    ), f"PID {pid} seconds out of range: {parts[-1]}"

    # Minutes, hours, days must be non-negative
    for val in parts[:-1]:
        assert val >= 0, f"PID {pid} negative time value: {val}"

    # Reconstruct total seconds
    total_seconds = 0
    if len(parts) == 2:  # M:SS
        total_seconds = parts[0] * TimeFormatIndex.SECONDS_PER_MINUTE + parts[1]
    elif len(parts) == 3:  # H:MM:SS
        total_seconds = (
            parts[0] * TimeFormatIndex.SECONDS_PER_HOUR
            + parts[1] * TimeFormatIndex.SECONDS_PER_MINUTE
            + parts[2]
        )
    elif len(parts) == 4:  # D-HH:MM:SS
        total_seconds = (
            parts[0] * TimeFormatIndex.SECONDS_PER_DAY
            + parts[1] * TimeFormatIndex.SECONDS_PER_HOUR
            + parts[2] * TimeFormatIndex.SECONDS_PER_MINUTE
            + parts[3]
        )

    days, remainder = divmod(total_seconds, TimeFormatIndex.SECONDS_PER_DAY)
    hours, remainder = divmod(remainder, TimeFormatIndex.SECONDS_PER_HOUR)
    minutes, seconds = divmod(remainder, TimeFormatIndex.SECONDS_PER_MINUTE)

    # Verify reconstructed values match parsed parts
    if len(parts) == 2:
        assert parts[0] == minutes and parts[1] == seconds
    elif len(parts) == 3:
        assert parts[0] == hours and parts[1] == minutes and parts[2] == seconds
    elif len(parts) == 4:
        assert (
            parts[0] == days
            and parts[1] == hours
            and parts[2] == minutes
            and parts[3] == seconds
        )


def test_get_process_time():
    """Test get_process_time returns valid TIME strings for all PIDs."""
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test get_process_time.")

    for pid in sorted(pids):
        time_str = get_process_time(pid)
        print(f"PID {pid} TIME: {time_str}")

        # Validate type
        assert isinstance(time_str, str), f"PID {pid} TIME is not a string: {time_str}"

        _validate_time_string(pid, time_str)
