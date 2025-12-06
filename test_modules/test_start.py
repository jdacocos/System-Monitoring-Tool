"""
test_start.py

Unit tests for start.py, verifying ps-style START column for all PIDs
and comparing results with psutil where possible.
"""

import time
import pytest
import psutil
from backend.process_util.pids import get_process_pids
from backend.process_util.start import get_process_start, _format_start_column


def _try_time_parse(s: str, fmt: str) -> bool:
    """
    Attempt to parse a string into a time.struct_time using a given format.
    """
    try:
        time.strptime(s, fmt)
        return True
    except ValueError:
        return False


def test_get_process_start_all_pids():
    """
    Test get_process_start for all PIDs listed in /proc.

    Validates:
      - Each PID returns a string.
      - START column is in one of the ps-style formats: HH:MM (today),
        MonDD (this year), or YYYY (previous years).
      - Comparison with psutil where accessible.

    Handles:
      - Skipping unreadable or exited PIDs.
      - Processes that psutil cannot access due to permissions.
      - Minor differences in formatting between our implementation and psutil.

    Prints START times for each PID when run with pytest -s for debugging.

    Raises:
        AssertionError: If the START string is not valid or differs significantly from psutil.
        pytest.skip: If no PIDs are available on the system.
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test get_process_start.")

    print("\nTesting all PIDs dynamically:")
    for pid in sorted(pids):
        start_str = get_process_start(pid)
        print(f"PID {pid} START: {start_str}")

        # Basic type check
        assert isinstance(start_str, str)
        if "Error" in start_str or start_str.strip() == "":
            continue  # skip unreadable/exited PIDs

        # Validate ps-style START formats
        valid_format = any(
            _try_time_parse(start_str, fmt) for fmt in ("%H:%M", "%b%d", "%Y")
        )
        assert valid_format, f"PID {pid} START has invalid format: {start_str}"

        # Compare with psutil if process exists
        try:
            ps_proc = psutil.Process(pid)
            ps_epoch = ps_proc.create_time()
            ps_start = _format_start_column(ps_epoch)
            print(f"PID {pid} psutil START: {ps_start}")

            # Allow for minor differences; match by string containment
            assert start_str in ps_start or ps_start in start_str
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
