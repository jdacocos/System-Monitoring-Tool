"""
test_command.py

This module contains unit tests for the `command.py` module, which provides
a function to retrieve the full command line (COMMAND) of processes
on a Linux system.

Tests are written using the pytest framework and validate that
`get_process_command`:

    - Returns a string for each PID
    - Handles non-existent or inaccessible processes gracefully
    - Returns non-empty strings for normal user processes
    - Handles kernel threads and empty cmdline cases properly

The tests iterate over all processes listed in `/proc` to ensure
robustness across a variety of system processes.

Requirements:
    pytest
"""

from process_util.command import get_process_command
from process_util.pids import get_process_pids


def test_get_process_command():
    """
    Test that get_process_command returns a valid string for all PIDs in /proc.

    Special cases:
        - '[PID not found]' if the PID disappears during the test
        - '[Permission denied]' if we can't read the process
        - '[zombie]' for zombie processes
        - '[kthread: <name>]' for kernel threads with empty cmdline
    """

    pids = get_process_pids()
    assert pids, "No PIDs found on this system to test get_process_command"

    for pid in sorted(pids):
        cmd = get_process_command(pid)
        print(f"PID {pid} COMMAND: '{cmd}'")

        # Must always be a string
        assert isinstance(cmd, str), f"PID {pid} returned non-string: {cmd}"

        # Allow placeholders for special cases
        if cmd in ("[PID not found]", "[Permission denied]", "[zombie]"):
            continue

        if cmd.startswith("[kthread:"):
            # Should include the kernel thread name
            assert (
                len(cmd) > 10
            ), f"PID {pid} returned malformed kernel thread command: {cmd}"
            continue

        # Normal user processes must have at least one character in the command
        assert len(cmd) > 0, f"PID {pid} returned empty command"
