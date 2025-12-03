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

# pylint: disable=redefined-outer-name

import pytest
import psutil
from process_struct import ProcessInfo
from process import populate_process_list


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
        f"{'START':<6} {'TIME':<8} COMMAND"
    )
    print("\n" + header)
    print("-" * len(header))
    for proc in processes:
        print(
            f"{proc.user:>8} {proc.pid:>5} {proc.cpu_percent:>5.1f} "
            f"{proc.mem_percent:>5.1f} {proc.vsz:>8} {proc.rss:>8} "
            f"{proc.tty:>7} {proc.stat:>5} {proc.start:>8} {proc.time:>8} "
            f"{proc.command}"
        )


def test_against_psutil(processes: list[ProcessInfo]) -> None:
    """
    Compare the ProcessInfo list against psutil's process list.
    Checks that at least the PIDs match and that key fields are reasonable.
    """
    # Get psutil PIDs
    psutil_pids = {p.pid for p in psutil.process_iter(["pid"])}

    # Get PIDs from your ProcessInfo
    custom_pids = {proc.pid for proc in processes}

    # There should be overlap
    assert (
        custom_pids & psutil_pids
    ), "No PIDs match between populate_process_list() and psutil"

    # Optional: check some fields for one sample process
    for proc in processes[:5]:  # check first 5 processes
        try:
            ps_proc = psutil.Process(proc.pid)
            # Check CPU and memory percentages are reasonably close
            cpu_diff = abs(proc.cpu_percent - ps_proc.cpu_percent(interval=0.0))
            mem_diff = abs(proc.mem_percent - ps_proc.memory_percent())
            assert cpu_diff < 50, f"CPU mismatch for PID {proc.pid}: {cpu_diff}"
            assert mem_diff < 50, f"Memory mismatch for PID {proc.pid}: {mem_diff}"
        except psutil.NoSuchProcess:
            # process may have terminated; skip
            continue
