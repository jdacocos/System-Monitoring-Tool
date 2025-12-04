"""
test_stat.py

Unit tests for stat.py, which interprets /proc/<pid>/stat
and produces human-readable process STAT strings.

Tests now compare the results with psutil where applicable.
"""

import pytest
import psutil
from backend.process_util.pids import get_process_pids
from backend.process_util.stat import get_process_stat

VALID_STATES = set("RSDZTtXxKWI")
VALID_FLAGS = set("s<NlL+")


def test_get_process_stat_all_pids():
    """
    Test get_process_stat() for all PIDs in /proc.
    Validates that:
      - Each PID returns a non-empty string
      - Base state matches psutil if accessible
      - Flags are within allowed set
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found to test process stat.")

    for pid in pids:
        stat_str = get_process_stat(pid)
        print(f"PID {pid}: stat = {stat_str}")

        # Basic type and non-empty
        assert isinstance(stat_str, str), f"PID {pid} stat should be string"
        assert len(stat_str) > 0, f"PID {pid} stat should not be empty"

        # Base state
        base_state = stat_str[0]
        assert (
            base_state in VALID_STATES
        ), f"PID {pid} base state '{base_state}' invalid"

        # Flags
        for c in stat_str[1:]:
            assert c in VALID_FLAGS, f"PID {pid} contains invalid flag '{c}'"

        # Compare base state with psutil if possible
        try:
            ps_proc = psutil.Process(pid)
            ps_status = ps_proc.status()  # returns 'running', 'sleeping', etc.

            # Map psutil status to single-letter STAT equivalent
            status_map = {
                "running": "R",
                "sleeping": "S",
                "disk_sleep": "D",
                "stopped": "T",
                "tracing_stop": "t",
                "zombie": "Z",
                "dead": "X",
                "wake_kill": "K",
                "waking": "W",
                "idle": "I",
            }
            ps_base = status_map.get(ps_status.lower(), None)
            if ps_base:
                assert (
                    base_state == ps_base
                ), f"PID {pid}: STAT base '{base_state}' != psutil '{ps_base}'"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Skip kernel or inaccessible processes
            continue
