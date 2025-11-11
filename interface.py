import curses
from pages.dashboard_page import render_dashboard
from pages.cpu_page import render_cpu
from pages.process_page import render_processes
from pages.memory_page import render_memory
from pages.network_page import render_network

def run_interface(stdscr: curses.window) -> None:
    curses.curs_set(0)
    curses.start_color()
    stdscr.nodelay(False)

    current_page = "dashboard"

    while True:
        if current_page == "dashboard":
            key = render_dashboard(stdscr)
        elif current_page == "cpu":
            key = render_cpu(stdscr)
        elif current_page == "processes":
            key = render_processes(stdscr)
        elif current_page == "network":
            key = render_network(stdscr)
        elif current_page == "memory":
            key = render_memory(stdscr)

        # Handle navigation
        if key == ord('q'):
            break
        elif key == ord('d'):
            current_page = "dashboard"
        elif key == ord('1'):
            current_page = "cpu"
        elif key == ord('2'):
            current_page = "processes"
        elif key == ord('3'):
            current_page = "network"
        elif key == ord('4'):
            current_page = "memory"
