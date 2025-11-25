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

from process_struct import ProcessInfo
from process import populate_process_list


def test_display_all_processes():
    """
    Retrieves all processes and prints a ps-aux style table.
    Includes zombies and kernel threads.
    """
    processes: list[ProcessInfo] = populate_process_list()

    # Header row
    header = (
        f"{'USER':<10} {'PID':<6} {'%CPU':>5} {'%MEM':>5} "
        f"{'VSZ':>8} {'RSS':>8} {'TTY':<8} {'STAT':<6} "
        f"{'START':<6} {'TIME':<8} COMMAND"
    )
    print(header)
    print("-" * len(header))

    for p in processes:
        print(
            f"{p.user:>8} {p.pid:>5} {p.cpu_percent:>5.1f} {p.mem_percent:>5.1f} "
            f"{p.vsz:>8} {p.rss:>8} {p.tty:>7} {p.stat:>5} {p.start:>8} {p.time:>8} "
            f"{p.command}"
        )
