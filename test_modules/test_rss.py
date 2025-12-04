"""
test_rss.py

Unit tests for rss.py, which provides functions for retrieving
process resident set size (RSS) and total system memory on Linux.

Tests are written using pytest and include:

    - Type and range checks for get_process_rss()
    - Validation of _read_meminfo_total()
    - Direct comparison with psutil for all PIDs
"""

import pytest
import psutil
from process_util.pids import get_process_pids
from process_util.rss import read_meminfo_total, get_process_rss


def test_read_meminfo_total():
    """Return total system memory and verify type and value"""
    total_mem = read_meminfo_total()
    print(f"Total system memory: {total_mem} KB")
    assert isinstance(total_mem, int)
    assert total_mem > 0  # should be positive on any system


def test_get_process_rss():
    """Test RSS retrieval for all PIDs in the system"""
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found to test RSS")

    for pid in pids:
        rss = get_process_rss(pid)
        print(f"PID {pid} RSS: {rss} KB")
        assert isinstance(rss, int)
        assert rss >= 0


def test_rss_against_psutil_all_pids():
    """
    Compare get_process_rss() results with psutil for all system PIDs.

    Notes:
        - Minor differences may occur due to timing or units.
        - Ensures no crashes occur for short-lived processes.
    """
    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found to test RSS against psutil")

    failed = []

    for pid in pids:
        try:
            rss_kb = get_process_rss(pid)
            psutil_rss_kb = psutil.Process(pid).memory_info().rss // 1024
            print(f"PID {pid}: my_rss={rss_kb} KB, psutil={psutil_rss_kb} KB")
            if abs(rss_kb - psutil_rss_kb) > 1024:
                failed.append((pid, rss_kb, psutil_rss_kb))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if failed:
        print(f"RSS comparison failed for {len(failed)} PIDs:")
        for pid, rss, ps_rss in failed:
            print(f"PID {pid}: my_rss={rss} KB, psutil={ps_rss} KB")
    assert not failed, "RSS values differ significantly from psutil for some PIDs"
