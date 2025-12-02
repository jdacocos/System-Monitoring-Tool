"""
test_rss.py

This module contains unit tests for rss.py, which provides functions
for retrieving process resident set size (RSS) and total system memory
on a Linux system.

Tests are written using the pytest framework. Each test validates that
the functions return correct types, expected value ranges, and handle
edge cases gracefully.

Key tests include:
    - Checking that get_process_rss returns a non-negative integer for
      existing PIDs.
    - Validating that _read_meminfo_total returns a reasonable system
      memory value in KB.

Requirements:
    pytest
"""

import pytest
from process_util.pids import get_process_pids
from process_util.rss import _read_meminfo_total, get_process_rss


def test_read_meminfo_total():
    """Test reading total system memory from /proc/meminfo"""
    total_mem = _read_meminfo_total()
    print(f"Total system memory: {total_mem} KB")
    assert total_mem > 0  # should be positive on any system


def test_get_process_rss():
    """
    Test reading resident set size (RSS) for all processes listed in /proc.
    Validates that RSS is a non-negative integer and prints the results.
    """
    pids = get_process_pids()
    assert pids, "No PIDs found to test RSS"

    for pid in pids:
        rss = get_process_rss(pid)
        print(f"PID {pid} RSS: {rss} KB")
        assert isinstance(rss, int), f"RSS for PID {pid} is not an int: {rss}"
        assert rss >= 0, f"RSS for PID {pid} should be non-negative, got {rss}"
