"""
Unit tests for memory_info module.
These tests compare output with psutil's virtual and swap memory stats.
"""

import psutil
from backend.memory_info import get_virtual_memory, get_swap_memory


def test_virtual_memory():
    """
    Validate that virtual memory stats match psutil.virtual_memory fields.
    Includes print statements for debugging when running pytest -s.
    """
    ours = get_virtual_memory()
    theirs = psutil.virtual_memory()

    print("\n=== Virtual Memory Comparison ===")
    print("Our virtual memory:", ours)
    print("Psutil virtual memory:", theirs)
    print("--------------------------------")

    assert ours.total == theirs.total
    assert ours.available == theirs.available
    assert ours.used is not None

    # Allow slight timing-based difference in used memory
    diff = abs(ours.used - theirs.used)
    print(f"Difference in used memory: {diff} bytes")

    assert diff < 50 * 1024 * 1024  # 50MB tolerance


def test_swap_memory():
    """
    Validate that swap memory stats match psutil.swap_memory fields.
    Includes print statements for debugging when running pytest -s.
    """
    ours = get_swap_memory()
    theirs = psutil.swap_memory()

    print("\n=== Swap Memory Comparison ===")
    print("Our swap memory:", ours)
    print("Psutil swap memory:", theirs)
    print("--------------------------------")

    assert ours.total == theirs.total
    assert ours.used is not None

    diff = abs(ours.used - theirs.used)
    print(f"Difference in swap used memory: {diff} bytes")

    assert diff < 50 * 1024 * 1024  # tolerance
