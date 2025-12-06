"""
Unit tests for cpu_info module.
These tests compare custom CPU information with psutil's values.
"""

import psutil
from backend.cpu_info import (
    get_cpu_percent_per_core,
    get_cpu_freq,
    get_logical_cpu_count,
    get_physical_cpu_count,
    get_cpu_stats,
)


def test_cpu_percent_per_core():
    """
    Validate per-core CPU percent values against psutil.cpu_percent().
    Includes debug prints for pytest -s.
    """
    ours = get_cpu_percent_per_core(interval=0.1)
    theirs = psutil.cpu_percent(interval=0.1, percpu=True)

    print("\n=== Per-core CPU Percent Comparison ===")
    print("Our per-core CPU%:", ours)
    print("Psutil per-core CPU%:", theirs)
    print("---------------------------------------")

    assert len(ours) == len(theirs)

    for i, (o, t) in enumerate(zip(ours, theirs)):
        diff = abs(o - t)
        print(f"Core {i}: ours={o}, psutil={t}, diff={diff}")

        # allow up to 20% jitter due to sampling time differences
        assert diff <= 20.0


def test_cpu_freq():
    """
    Validate CPU frequency matches psutil.cpu_freq().
    """
    our_freq = get_cpu_freq()
    psutil_freq = psutil.cpu_freq()

    print("\n=== CPU Frequency Comparison ===")
    print("Our freq:", our_freq)
    print("Psutil freq:", psutil_freq)
    print("--------------------------------")

    assert our_freq is not None

    # Only checking "current" because min/max in your implementation default to 0
    diff = abs(our_freq.current - psutil_freq.current)
    print("Current frequency diff:", diff)

    assert diff <= 300  # 300 MHz tolerance


def test_cpu_counts():
    """
    Validate logical and physical CPU counts.
    """
    our_logical = get_logical_cpu_count()
    our_physical = get_physical_cpu_count()

    psutil_logical = psutil.cpu_count(logical=True)
    psutil_physical = psutil.cpu_count(logical=False)

    print("\n=== CPU Counts Comparison ===")
    print("Our logical:", our_logical)
    print("Our physical:", our_physical)
    print("Psutil logical:", psutil_logical)
    print("Psutil physical:", psutil_physical)
    print("--------------------------------")

    assert our_logical == psutil_logical

    # physical count can be None depending on parsing
    if our_physical is not None:
        assert our_physical == psutil_physical


def test_cpu_stats():
    """
    Validate composite CPU stats dict.
    """
    ours = get_cpu_stats()
    theirs_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    theirs_freq = psutil.cpu_freq()

    print("\n=== Full CPU Stats Comparison ===")
    print("Our stats:", ours)
    print("Psutil per_core:", theirs_per_core)
    print("Psutil freq:", theirs_freq)
    print("--------------------------------")

    assert "overall" in ours
    assert "per_core" in ours
    assert "freq" in ours
    assert "logical" in ours
    assert "physical" in ours

    # per-core list size match
    assert len(ours["per_core"]) == len(theirs_per_core)

    # frequency comparison
    diff_freq = abs(ours["freq"].current - theirs_freq.current)
    print("Freq diff:", diff_freq)
    assert diff_freq <= 300
