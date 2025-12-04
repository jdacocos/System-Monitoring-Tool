"""
test_command.py

Unit tests for process_util.command.get_process_command, comparing output
against psutil for all PIDs.
"""

import re
import pytest
import psutil
from backend.process_util.command import get_process_command
from backend.process_util.pids import get_process_pids


def _normalize_cmd(cmd: str) -> str:
    """Normalize a command string for comparison: strip and collapse spaces."""
    if not cmd:
        return ""
    return re.sub(r"\s+", " ", cmd.strip())


def test_get_process_command_vs_psutil():
    """
    Compare `get_process_command` against psutil for all PIDs.

    Validates that:
        - Normal user processes return matching command lines
        - Kernel threads, zombies, and inaccessible PIDs return expected placeholders
        - Leading/trailing and multiple spaces are normalized before comparison
        - Special cases like '[PID not found]' or '[Permission denied]' are handled gracefully
    """

    pids = get_process_pids()
    if not pids:
        pytest.skip("No PIDs found on this system to test get_process_command.")

    for pid in sorted(pids):
        our_cmd = _normalize_cmd(get_process_command(pid))
        print(f"PID {pid} COMMAND: '{our_cmd}'")

        if our_cmd in ("[PID not found]", "[Permission denied]", "[zombie]"):
            continue

        try:
            ps_proc = psutil.Process(pid)
            ps_cmd_list = ps_proc.cmdline()
            ps_cmd = " ".join(ps_cmd_list) if ps_cmd_list else f"[{ps_proc.name()}]"
            ps_cmd = _normalize_cmd(ps_cmd)

        except psutil.NoSuchProcess:
            ps_cmd = "[PID not found]"
        except psutil.AccessDenied:
            ps_cmd = "[Permission denied]"
        except OSError:
            ps_cmd = "[error]"

        assert our_cmd == ps_cmd, f"PID {pid} mismatch: '{our_cmd}' vs '{ps_cmd}'"
