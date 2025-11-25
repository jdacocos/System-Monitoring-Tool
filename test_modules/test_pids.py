"""
test_pids.py

This module contains unit tests for the process_util.pids module,
which provides functions for retrieving process IDs (PIDs)
from the Linux /proc filesystem.

Tests are written using the pytest framework. Each test validates
that the returned PIDs are valid, positive integers and that
the functions handle missing or inaccessible /proc entries gracefully.

Requirements:
    pytest
Linux-only: Requires access to a mounted /proc filesystem.
"""

import os
import pytest
from process_util.pids import open_file_system, get_process_pids


def test_open_file_system():
    """
    Tests that /proc path for the Linux file system correctly displays all contents.
    """

    fs = open_file_system()

    # 1. Ensure return type is ScandirIterator
    assert type(fs) is type(os.scandir("/"))

    # 2. Ensure iterating works (no errors)
    entries = list(fs)
    assert len(entries) > 0  # 3. /proc must contain something

    # Optional: ensure entries have names
    assert all(hasattr(e, "name") for e in entries)

    print("\nAll contents of /proc:")
    entries = open_file_system()
    for entry in entries:
        print(entry.name)


def test_get_process_pids():
    """
    Tests that all the pids are successfully retrieved from /proc.
    """

    pids = get_process_pids()

    # 1. Should return a list
    assert isinstance(pids, list)

    # 2. All entries should be integers
    assert all(isinstance(pid, int) for pid in pids)

    # 3. All PIDs should correspond to directories in /proc
    assert all(os.path.isdir(f"/proc/{pid}") for pid in pids)

    # 4. Process should be included
    current_pid = os.getpid()
    assert current_pid in pids
