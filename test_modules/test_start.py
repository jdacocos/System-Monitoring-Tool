"""
test_start.py

Unit tests for start.py, verifying ps-style START column for all PIDs
and comparing results with psutil where possible.
"""

import time
import pytest
import psutil
from backend.process_util.pids import get_process_pids
from backend.process_util.start import get_process_start


def _try_time_parse(s: str, fmt: str) -> bool:
    try:
        time.strptime(s, fmt)
        return True
    except ValueError:
        return False


def _format_psutil_start(epoch_seconds: float) -> str:
    """
    Format psutil start time similar to ps-style START column.
    """
    start_tm = time.localtime(epoch_seconds)
    now_tm = time.localtime(time.time())

    if start_tm.tm_year == now_tm.tm_year and start_tm.tm_yday == now_tm.tm_yday:
        return time.strftime("%H:%M", start_tm)

    if start_tm.tm_year == now_tm.tm_year:
        return time.strftime("%b%d", start_tm)

    return str(start_tm.tm_year)


def test_get_process_start_all_pids():
    """
    Test get_process_start for all PIDs listed in /proc.

    Validates:
      - Each PID returns a string.
      - START column is in one of the ps-style formats: HH:MM, MonDD, or YYYY.
      - Comparison with psutil where accessible.
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
            continue  # skip unreadable/exited PIDs

        # Validate ps-style START formats
        valid_format = any(
            time.strptime(start_str, fmt)
            for fmt in ("%H:%M", "%b%d", "%Y")
            if _try_time_parse(start_str, fmt)
        )
        assert valid_format, f"PID {pid} START has invalid format: {start_str}"

        # Compare with psutil if process exists
        try:
            ps_proc = psutil.Process(pid)
            ps_epoch = ps_proc.create_time()
            ps_start = _format_psutil_start(ps_epoch)
            print(f"PID {pid} psutil START: {ps_start}")

            # Allow for minor differences due to rounding; match by string prefix
            assert start_str in ps_start or ps_start in start_str
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue  # skip processes psutil cannot access
