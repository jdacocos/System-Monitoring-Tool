"""
interface.py

Main entry point for the interactive terminal UI.

Provides a curses-based interface for navigating between different system
monitoring pages: Dashboard, CPU, Processes, Network, Memory, and Disk I/O.

Shows:
- Keyboard navigation between pages using assigned keys
- Handles page rendering and switching
- Exits cleanly on 'q' or 'Q'

Integrates with the generic page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes

Dependencies:
- curses (standard library)
- frontend.pages.dashboard_page.render_dashboard
- frontend.pages.cpu_page.render_cpu
- frontend.pages.process_page.process_page.render_processes
- frontend.pages.memory_page.render_memory
- frontend.pages.network_page.render_network
- frontend.pages.disk_page.render_disk
"""

import curses
from frontend.pages.dashboard_page import render_dashboard
from frontend.pages.cpu_page import render_cpu
from frontend.pages.process_page.process_page import render_processes
from frontend.pages.memory_page import render_memory
from frontend.pages.network_page import render_network
from frontend.pages.disk_page import render_disk

NAV_ITEMS: list[tuple[str, str, str]] = [
    ("dashboard", "Dashboard", "d"),
    ("cpu", "CPU", "1"),
    ("processes", "Processes", "2"),
    ("network", "Network", "3"),
    ("memory", "Memory", "4"),
    ("disk", "Disk I/O", "5"),
]


KEY_TO_PAGE = {
    ord("d"): "dashboard",
    ord("D"): "dashboard",
    ord("1"): "cpu",
    ord("2"): "processes",
    ord("3"): "network",
    ord("4"): "memory",
    ord("5"): "disk",
}


def run_interface(stdscr: curses.window) -> None:
    """
    Start the interactive curses-based system monitoring interface.

    This function initializes curses settings and enters the main loop,
    rendering the currently active page and handling user input to
    navigate between pages or quit the application.

    Parameters:
        stdscr : curses.window
        The main curses window provided by curses.wrapper.

    Returns:
    None
    """
    curses.curs_set(0)
    curses.start_color()
    stdscr.nodelay(False)

    current_page = "dashboard"

    while True:
        if current_page == "dashboard":
            key = render_dashboard(stdscr, NAV_ITEMS, current_page)
        elif current_page == "cpu":
            key = render_cpu(stdscr, NAV_ITEMS, current_page)
        elif current_page == "processes":
            key = render_processes(stdscr, NAV_ITEMS, current_page)
        elif current_page == "network":
            key = render_network(stdscr, NAV_ITEMS, current_page)
        elif current_page == "memory":
            key = render_memory(stdscr, NAV_ITEMS, current_page)
        elif current_page == "disk":
            key = render_disk(stdscr, NAV_ITEMS, current_page)
        else:
            key = ord("q")

        if key in (ord("q"), ord("Q")):
            break
        if key in KEY_TO_PAGE:
            current_page = KEY_TO_PAGE[key]
