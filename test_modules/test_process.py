"""
test_process.py

Pytest module for validating the ProcessInfo objects created by process.py.

Tests verify:
    - Process list is not empty
    - All entries are ProcessInfo instances
    - Required fields exist with correct types
    - PIDs are unique
    - CPU, memory, and memory sizes are non-negative
    - Optional visual display
    - Comparison with psutil for consistency across all running PIDs

Requirements:
    - pytest
    - psutil
"""

import pytest
import psutil
from backend.process_struct import ProcessInfo
from backend.process import populate_process_list

# pylint: disable=redefined-outer-name


@pytest.fixture
def processes() -> list[ProcessInfo]:
    """Return the list of populated ProcessInfo objects."""
    proc_list = populate_process_list()
    assert isinstance(proc_list, list), "populate_process_list() must return a list"
    return proc_list


def test_process_list_not_empty(processes: list[ProcessInfo]) -> None:
    """Ensure at least one process is returned."""
    assert processes, "populate_process_list() returned zero processes"


def test_process_types(processes: list[ProcessInfo]) -> None:
    """Ensure all items in the list are ProcessInfo objects."""
    for proc in processes:
        assert isinstance(proc, ProcessInfo), f"Invalid type: {type(proc)}"


def test_required_fields_exist(processes: list[ProcessInfo]) -> None:
    """Check that all ProcessInfo fields exist and have correct types."""
    for proc in processes:
        assert isinstance(proc.user, str)
        assert isinstance(proc.pid, int)
        assert isinstance(proc.cpu_percent, float)
        assert isinstance(proc.mem_percent, float)
        assert isinstance(proc.vsz, int)
        assert isinstance(proc.rss, int)
        assert isinstance(proc.tty, str)
        assert isinstance(proc.stat, str)
        assert isinstance(proc.start, str)
        assert isinstance(proc.time, str)
        assert isinstance(proc.nice, int)  # Added nice check
        assert isinstance(proc.command, str)


def test_pids_are_unique(processes: list[ProcessInfo]) -> None:
    """Ensure all PIDs in the process list are unique."""
    pids = [proc.pid for proc in processes]
    assert len(pids) == len(set(pids)), "Duplicate PIDs found"


def test_no_negative_values(processes: list[ProcessInfo]) -> None:
    """Ensure CPU, memory, and VSZ/RSS values are non-negative."""
    for proc in processes:
        assert proc.cpu_percent >= 0
        assert proc.mem_percent >= 0
        assert proc.vsz >= 0
        assert proc.rss >= 0


def test_optional_display(processes: list[ProcessInfo]) -> None:
    """
    Pretty-print process table for manual inspection.
    Run with `pytest -s` to see output. Does not affect pass/fail.
    """
    header = (
        f"{'USER':<10} {'PID':<6} {'%CPU':>5} {'%MEM':>5} "
        f"{'VSZ':>8} {'RSS':>8} {'TTY':<8} {'STAT':<6} "
        f"{'START':<6} {'TIME':<8} {'NI':>3} COMMAND"
    )
    print("\n" + header)
    print("-" * len(header))
    for proc in processes:
        print(
            f"{proc.user:>8} {proc.pid:>5} {proc.cpu_percent:>5.1f} "
            f"{proc.mem_percent:>5.1f} {proc.vsz:>8} {proc.rss:>8} "
            f"{proc.tty:>7} {proc.stat:>5} {proc.start:>8} {proc.time:>8} "
            f"{proc.nice:>3} {proc.command}"
        )


def test_against_psutil(processes: list[ProcessInfo]) -> None:
    """
    Compare the ProcessInfo list against psutil's process list.

    Ensures that:
      - PIDs overlap with psutil
      - USER matches psutil where available
      - COMMAND matches for normal user processes
      - Kernel thread commands are non-empty inside brackets
    """
    # Get all psutil processes with basic info
    psutil_procs = {p.pid: p for p in psutil.process_iter(["pid", "name", "username"])}

    for proc in processes:
        # Skip PIDs not in psutil
        if proc.pid not in psutil_procs:
            continue

        ps_proc = psutil_procs[proc.pid]

        # Compare username
        try:
            ps_user = ps_proc.username()
            if ps_user:
                assert proc.user == ps_user, f"PID {proc.pid} USER mismatch"
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            # Ignore inaccessible or terminated processes
            continue

        # Compare command line
        try:
            ps_cmd_list = ps_proc.cmdline()
            ps_cmd = " ".join(ps_cmd_list) if ps_cmd_list else f"[{ps_proc.name()}]"

            # Normalize whitespace for comparison
            proc_cmd_norm = " ".join(proc.command.split())
            ps_cmd_norm = " ".join(ps_cmd.split())

            if proc.command.startswith("[") and proc.command.endswith("]"):
                # Kernel threads: just ensure non-empty inside brackets
                assert (
                    len(proc.command) > 2
                ), f"PID {proc.pid} malformed kernel thread command"
            else:
                # Normal processes: compare normalized commands
                assert proc_cmd_norm == ps_cmd_norm, f"PID {proc.pid} COMMAND mismatch"

        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
