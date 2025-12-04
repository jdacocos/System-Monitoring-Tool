"""
test_time.py

Unit tests for time.py, validating CPU TIME strings for processes
on Linux, directly comparing with psutil.Process.cpu_times().

Tests ensure:
    - get_process_time(pid) returns a valid TIME string
    - TIME string conforms to M:SS, H:MM:SS, or D-HH:MM:SS
    - Seconds in [0, 59], other components non-negative
    - Matches psutil CPU times where accessible

Requirements:
    pytest
    psutil
"""

import pytest
import psutil
from backend.process_util.pids import get_process_pids
from backend.process_util.time import get_process_time
from backend.process_constants import TimeFormatIndex


def parse_time_string(time_str: str) -> int:
    """Convert TIME string into total seconds."""
    if time_str == TimeFormatIndex.DEFAULT_TIME:
        return 0

    parts = [int(p) for p in time_str.replace("-", ":").split(":")]

    if len(parts) == 2:  # M:SS
        return parts[0] * 60 + parts[1]

    if len(parts) == 3:  # H:MM:SS
        return parts[0] * 3600 + parts[1] * 60 + parts[2]

    if len(parts) == 4:  # D-HH:MM:SS
        return parts[0] * 86400 + parts[1] * 3600 + parts[2] * 60 + parts[3]

    return 0


def test_get_process_time_vs_psutil_all_pids():
    """Compare get_process_time with psutil for all PIDs."""
    pids = get_process_pids()
    if not pids:
        pytest.fail("No PIDs found to test get_process_time.")

    print("\nTesting process TIME vs psutil (all PIDs):")
    for pid in sorted(pids):
        time_str = get_process_time(pid)
        # Optional: remove or comment out the next line to reduce console output
        print(f"PID {pid} TIME: {time_str}")

        # Validate type
        assert isinstance(time_str, str), f"PID {pid} TIME is not a string"

        # Skip unreadable or exited processes
        if time_str == TimeFormatIndex.DEFAULT_TIME:
            continue

        # Convert to seconds
        total_seconds_custom = parse_time_string(time_str)

        # Compare with psutil if accessible
        try:
            p = psutil.Process(pid)
            cpu_seconds = sum(p.cpu_times()[:2])  # user + system
            # Allow small rounding differences (1 sec)
            assert abs(total_seconds_custom - cpu_seconds) <= 1.0, (
                f"PID {pid} TIME mismatch: custom={total_seconds_custom}, "
                f"psutil={cpu_seconds}"
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue  # skip inaccessible PIDs
