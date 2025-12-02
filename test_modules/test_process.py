"""
test_process.py

This pytest module retrieves and displays all running processes
on the system using the ProcessInfo dataclass and the populate_process_list()
function.

It prints the process list in a format similar to the 'ps aux' command,
including the following columns:

    USER, PID, %CPU, %MEM, VSZ, RSS, TTY, STAT, START, TIME, COMMAND

Purpose:
    - Manual inspection of the ProcessInfo population
    - Visual verification that all getters for process attributes
      are working correctly
    - Provides a reference layout for automated unit tests in the future

Requirements:
    - pytest
    - The process.py module with a working populate_process_list() function
"""

import pytest
from process_struct import ProcessInfo
from process import populate_process_list


@pytest.fixture
def processes() -> list[ProcessInfo]:
    """Returns the populated process list."""
    procs = populate_process_list()
    assert isinstance(procs, list)
    return procs


def test_process_list_not_empty(processes):
    """Ensure at least one process is returned."""
    assert len(processes) > 0, "populate_process_list() returned zero processes"


def test_process_types(processes):
    """Ensure the list contains only ProcessInfo objects."""
    for p in processes:
        assert isinstance(p, ProcessInfo), f"Invalid type: {type(p)}"


def test_required_fields_exist(processes):
    """Check all fields of ProcessInfo are populated with valid types."""
    for p in processes:
        assert isinstance(p.user, str)
        assert isinstance(p.pid, int)
        assert isinstance(p.cpu_percent, float)
        assert isinstance(p.mem_percent, float)
        assert isinstance(p.vsz, int)
        assert isinstance(p.rss, int)
        assert isinstance(p.tty, str)
        assert isinstance(p.stat, str)
        assert isinstance(p.start, str)
        assert isinstance(p.time, str)
        assert isinstance(p.command, str)


def test_pids_are_unique(processes):
    """Ensure PIDs in the process list are unique."""
    pids = [p.pid for p in processes]
    assert len(pids) == len(set(pids)), "Duplicate PIDs found in results"


def test_no_negative_values(processes):
    """Ensure memory and CPU stats are not negative."""
    for p in processes:
        assert p.cpu_percent >= 0
        assert p.mem_percent >= 0
        assert p.vsz >= 0
        assert p.rss >= 0


def test_optional_display(processes):
    """
    Pretty print table when running with pytest -s.
    This does NOT affect pass/fail results.
    """
    header = (
        f"{'USER':<10} {'PID':<6} {'%CPU':>5} {'%MEM':>5} "
        f"{'VSZ':>8} {'RSS':>8} {'TTY':<8} {'STAT':<6} "
        f"{'START':<6} {'TIME':<8} COMMAND"
    )
    print("\n" + header)
    print("-" * len(header))

    for p in processes:
        print(
            f"{p.user:>8} {p.pid:>5} {p.cpu_percent:>5.1f} {p.mem_percent:>5.1f} "
            f"{p.vsz:>8} {p.rss:>8} {p.tty:>7} {p.stat:>5} {p.start:>8} {p.time:>8} "
            f"{p.command}"
        )
