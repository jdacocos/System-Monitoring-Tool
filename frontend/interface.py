import curses
from frontend.pages.dashboard_page import render_dashboard
from frontend.pages.cpu_page import render_cpu
from frontend.pages.process_page import render_processes
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
    """Entry point for the interactive curses interface."""

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
