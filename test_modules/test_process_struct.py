"""
test_process_struct.py

This module contains unit tests for the process_struct.py module,
which defines the ProcessInfo dataclass representing a system process
with attributes such as user, PID, CPU and memory usage, and command.

Tests verify that the dataclass correctly validates field values,
handles edge cases, and maintains the expected types and ranges
for CPU and memory percentages, PID, and other attributes.

Tests are written using the pytest framework.

Requirements:
    pytest
"""
import pytest
from process_struct import ProcessInfo

def test_process_info_creation():

    """Test that ProcessInfo can be created and fields are readable."""

    p = ProcessInfo(
        user="root",
        pid=1234,
        cpu_percent=12.5,
        mem_percent=45.3,
        vsz=1048576,
        rss=204800,
        tty="?",
        stat="S",
        start="12:34",
        time="00:01:23",
        command="/usr/bin/python3"
    )

    # Print each field for verification
    print(f"\nuser: {p.user}")
    print(f"pid: {p.pid}")
    print(f"cpu_percent: {p.cpu_percent}")
    print(f"mem_percent: {p.mem_percent}")
    print(f"vsz: {p.vsz}")
    print(f"rss: {p.rss}")
    print(f"tty: {p.tty}")
    print(f"stat: {p.stat}")
    print(f"start: {p.start}")
    print(f"time: {p.time}")
    print(f"command: {p.command}")
    
    assert p.user == "root"
    assert p.pid == 1234
    assert isinstance(p.cpu_percent, float)
    assert isinstance(p.mem_percent, float)
    assert p.vsz == 1048576
    assert p.rss == 204800
    assert p.tty == "?"
    assert p.stat == "S"
    assert p.start == "12:34"
    assert p.time == "00:01:23"
    assert p.command == "/usr/bin/python3"

    # Optional: test string representation
    s = str(p)
    assert "ProcessInfo" in s
    assert "root" in s
    assert "1234" in s


# ------------------------------------------------------------
# Expected failure test
@pytest.mark.xfail(reason="PID should not accept negative numbers yet")
def test_process_info_invalid_pid():

    """This test is expected to fail for now."""

    p = ProcessInfo(
        user="root",
        pid=-1,  # Invalid PID
        cpu_percent=0.0,
        mem_percent=0.0,
        vsz=0,
        rss=0,
        tty="?",
        stat="S",
        start="00:00",
        time="00:00:00",
        command="invalid"
    )
    assert p.pid > 0  # This will fail, marked as xfail


# ------------------------------------------------------------
# Test that an exception is raised
def test_invalid_cpu_percent():

    """CPU percent must be float between 0 and 100."""

    with pytest.raises(ValueError):
        p = ProcessInfo(
            user="root",
            pid=1234,
            cpu_percent=150.0,  # Invalid
            mem_percent=10.0,
            vsz=1000,
            rss=100,
            tty="?",
            stat="S",
            start="00:00",
            time="00:00:01",
            command="python"
        )


# ------------------------------------------------------------
# Parameterized test example
@pytest.mark.parametrize(
    "user, pid",
    [
        ("root", 1),
        ("nobody", 100),
        ("daemon", 2000),
    ]
)
def test_multiple_processes(user, pid):
    p = ProcessInfo(
        user=user,
        pid=pid,
        cpu_percent=0.0,
        mem_percent=0.0,
        vsz=1000,
        rss=100,
        tty="?",
        stat="S",
        start="00:00",
        time="00:00:01",
        command="python"
    )

    print(f"\nTesting ProcessInfo(user={p.user}, pid={p.pid})")

    assert p.user == user
    assert p.pid == pid
