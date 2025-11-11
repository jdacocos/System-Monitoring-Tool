# pages/process_page.py
import curses
import psutil
import time
from utils.ui_helpers import init_colors, draw_title, draw_box, draw_footer, draw_section_header
from utils.input_helpers import handle_input, GLOBAL_KEYS


def get_process_data() -> tuple[list[dict], list[dict]]:
    """Fetch and return top 5 processes by CPU and memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    valid_cpu = [p for p in processes if p['cpu_percent'] is not None]
    valid_mem = [p for p in processes if p['memory_percent'] is not None]

    top_cpu = sorted(valid_cpu, key=lambda p: p['cpu_percent'], reverse=True)[:5]
    top_mem = sorted(valid_mem, key=lambda p: p['memory_percent'], reverse=True)[:5]

    return top_cpu, top_mem


def render_cpu_table(stdscr: curses.window, top_cpu: list[dict]) -> None:
    """Render the top CPU-consuming processes."""
    draw_section_header(stdscr, 2, "Top 5 Processes by CPU Usage")
    stdscr.addstr(3, 4, "PID     NAME                          CPU%")
    stdscr.hline(4, 4, "-", 50)

    for i, p in enumerate(top_cpu):
        if p['cpu_percent'] < 50:
            color = 3
        else:
            color = 4

        stdscr.attron(curses.color_pair(color))
        stdscr.addstr(5 + i, 4, f"{p['pid']:<7} {p['name'][:28]:<28} {p['cpu_percent']:>5.1f}")
        stdscr.attroff(curses.color_pair(color))


def render_memory_table(stdscr: curses.window, top_mem: list[dict]) -> None:
    """Render the top memory-consuming processes."""
    start_y = 12
    draw_section_header(stdscr, start_y, "Top 5 Processes by Memory Usage")
    stdscr.addstr(start_y + 1, 4, "PID     NAME                          MEM%")
    stdscr.hline(start_y + 2, 4, "-", 50)

    for i, p in enumerate(top_mem):
        if p['memory_percent'] < 20:
            color = 3
        else:
            color = 4

        stdscr.attron(curses.color_pair(color))
        stdscr.addstr(start_y + 3 + i, 4, f"{p['pid']:<7} {p['name'][:28]:<28} {p['memory_percent']:>5.1f}")
        stdscr.attroff(curses.color_pair(color))


def render_processes(stdscr: curses.window) -> int:
    """
    Render the Process Monitor page showing top CPU and Memory consuming processes.
    Returns the pressed key for navigation.
    """
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        stdscr.erase()
        stdscr.bkgd(' ', curses.color_pair(1))
        draw_title(stdscr, "PROCESS MONITOR")
        draw_box(stdscr)

        top_cpu, top_mem = get_process_data()
        render_cpu_table(stdscr, top_cpu)
        render_memory_table(stdscr, top_mem)

        draw_footer(stdscr)
        stdscr.refresh()

        key = handle_input(stdscr, GLOBAL_KEYS)
        if key != -1:
            return key

        time.sleep(0.5)