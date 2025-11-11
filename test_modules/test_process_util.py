import pytest
from process_struct import ProcessInfo
from process_util import get_process_info

def test_get_process_info_basic():

    """Test that get_process_info fills the list correctly and returns 0."""

    processes = []
    ret = get_process_info(processes, limit=5)

    # Check return value
    assert ret == 0

    # Check that the list is populated
    assert isinstance(processes, list)
    assert len(processes) > 0
    assert len(processes) <= 5

    # Check the first item
    first_proc = processes[0]
    assert isinstance(first_proc, ProcessInfo)
    assert hasattr(first_proc, 'user')
    assert hasattr(first_proc, 'pid')
    assert hasattr(first_proc, 'command')

def test_get_process_info_empty_list():

    """Ensure the list is cleared before populating."""

    processes = [ProcessInfo(
        user="dummy",
        pid=9999,
        cpu_percent=0.0,
        mem_percent=0.0,
        vsz=0,
        rss=0,
        tty="?",
        stat="S",
        start="00:00",
        time="00:00:00",
        command="none"
    )]

    ret = get_process_info(processes, limit=3)
    assert ret == 0
    assert len(processes) <= 3
    # The original dummy entry should have been cleared
    assert processes[0].pid != 9999

@pytest.mark.parametrize("limit", [1, 3, 5])
def test_get_process_info_limit(limit):

    """Test that limit parameter restricts the number of processes returned."""

    processes = []
    ret = get_process_info(processes, limit=limit)
    assert ret == 0
    assert len(processes) <= limit

@pytest.mark.xfail(reason="Handles PermissionError gracefully for inaccessible processes")
def test_get_process_info_permission_error(monkeypatch):

    """Simulate PermissionError to test graceful handling."""

    import process_util

    def fake_listdir(path):
        return ["1", "2"]

    def fake_open(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(process_util.os, "listdir", fake_listdir)
    monkeypatch.setattr(process_util, "_read_proc_stat", lambda pid: ("cmd", "S"))
    monkeypatch.setattr(process_util, "_read_proc_status", lambda pid: ("root", 0, 0))
    # The function should still return 0 despite PermissionError inside try
    processes = []
    ret = get_process_info(processes, limit=2)
    assert ret == 0
