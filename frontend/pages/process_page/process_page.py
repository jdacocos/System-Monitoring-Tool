"""
pages/process_page.py

Provides an interactive process manager UI using curses.

Displays a scrollable list of processes with CPU, memory, VSZ, RSS, TTY,
STAT, start time, elapsed time, and command.

Features:
- Sorting by CPU, memory, PID, or name
- Navigation with arrow keys
- Kill a process
- Refresh interval handling
"""

import curses
import os
import time
from typing import List, Optional, Tuple

from frontend.utils.ui_helpers import (
    init_colors,
    draw_content_window,
    draw_section_header
)
from frontend.utils.input_helpers import handle_input, GLOBAL_KEYS
from backend.process import populate_process_list
from backend.process_struct import ProcessInfo
from frontend.pages.process_page.process_page_constants import (
    COL_WIDTHS,
    SORT_KEYS,
    CRITICAL_PROCESSES,
    REFRESH_INTERVAL,
    DRAW_INTERVAL,
    INPUT_TIMEOUT,
    ERROR_DISPLAY_TIME,
    PAGE_JUMP_SIZE,
    KILL_RETRY_DELAY,
    SIGTERM,
    SIGKILL,
    SIG_CHECK,
    HEADER_ROW,
    SEPARATOR_ROW,
    FIRST_DATA_ROW,
    SECTION_HEADER_ROW,
    FOOTER_OFFSET,
    VISIBLE_LINE_OFFSET,
    COLOR_ERROR,
    COLOR_FOOTER,
    COLOR_WARNING,
    COLOR_NORMAL,
    COLOR_SELECTED,
)


def is_critical_process(proc: ProcessInfo) -> bool:
    """Check if a process is critical (dangerous to kill)."""
    if not proc.command:
        return False

    cmd = _extract_command_name(proc.command)

    # Check if it matches any critical process
    for critical in CRITICAL_PROCESSES:
        if cmd.startswith(critical) or cmd == critical:
            return True

    # Also check for PID 1 (init)
    return proc.pid == 1


def _extract_command_name(command: str) -> str:
    """
    Extract base command name from full command string.
    
    Helper: Removes path prefixes, leading dashes (login shells),
    and command arguments to get just the base command name.
    """
    cmd = command.strip()

    # Remove leading dash (for login shells like -bash, -zsh, etc.)
    if cmd.startswith('-'):
        cmd = cmd[1:]

    if '/' in cmd:
        cmd = cmd.split('/')[-1]  # Get just the filename

    cmd = cmd.split()[0]  # Get just the command without args

    return cmd


def get_all_processes(sort_mode: str = "cpu") -> List[ProcessInfo]:
    """Return all processes sorted by the given sort_mode."""
    processes = populate_process_list()
    sort_attr = SORT_KEYS.get(sort_mode, "cpu_percent")
    reverse = sort_attr in ("cpu_percent", "mem_percent")
    processes.sort(key=lambda p: getattr(p, sort_attr, 0), reverse=reverse)
    return processes


def _get_process_color(proc: ProcessInfo, is_selected: bool) -> int:
    """
    Determine the color pair for a process based on its state.
    
    Helper: Returns appropriate color for critical/normal processes
    and selected/unselected states.
    """
    is_critical = is_critical_process(proc)

    if is_selected:
        return COLOR_ERROR if is_critical else COLOR_SELECTED

    return COLOR_WARNING if is_critical else COLOR_NORMAL


def _format_process_line(proc: ProcessInfo, width: int) -> str:
    """
    Format a process info into a display line.
    
    Helper: Creates a formatted string with all process information
    aligned according to column widths.
    """
    tty_display = (proc.tty or "?")[: COL_WIDTHS["tty"] - 1]
    used_width = sum(COL_WIDTHS.values())
    command_width = max(10, width - 4 - used_width)
    command_display = (proc.command or "")[:command_width]

    return (
        f"{proc.user:<{COL_WIDTHS['user']}} "
        f"{proc.pid:<{COL_WIDTHS['pid']}} "
        f"{proc.cpu_percent:>{COL_WIDTHS['cpu']}.1f} "
        f"{proc.mem_percent:>{COL_WIDTHS['mem']}.1f} "
        f"{proc.vsz:>{COL_WIDTHS['vsz']}} "
        f"{proc.rss:>{COL_WIDTHS['rss']}} "
        f"{tty_display:<{COL_WIDTHS['tty']}} "
        f"{proc.stat:<{COL_WIDTHS['stat']}} "
        f"{proc.start:<{COL_WIDTHS['start']}} "
        f"{proc.time:<{COL_WIDTHS['time']}} "
        f"{command_display}"
    )


def draw_process_row(
    win: curses.window, y: int, proc: ProcessInfo, width: int, is_selected: bool
):
    """Draw a single process row in the window."""
    line = _format_process_line(proc, width)
    color_pair = _get_process_color(proc, is_selected)

    try:
        win.attron(curses.color_pair(color_pair))
        win.addnstr(y, 2, line, width - 3)
        win.attroff(curses.color_pair(color_pair))
    except curses.error:
        pass


def _format_header() -> str:
    """
    Format the process list header.
    
    Helper: Creates column headers with proper spacing and alignment.
    """
    header_fmt = (
        f"{{user:<{COL_WIDTHS['user']}}} {{pid:<{COL_WIDTHS['pid']}}} "
        f"{{cpu:>{COL_WIDTHS['cpu']}}} {{mem:>{COL_WIDTHS['mem']}}} "
        f"{{vsz:>{COL_WIDTHS['vsz']}}} {{rss:>{COL_WIDTHS['rss']}}} "
        f"{{tty:<{COL_WIDTHS['tty']}}} {{stat:<{COL_WIDTHS['stat']}}} "
        f"{{start:<{COL_WIDTHS['start']}}} {{time:<{COL_WIDTHS['time']}}} COMMAND"
    )
    return header_fmt.format(
        user="USER",
        pid="PID",
        cpu="%CPU",
        mem="%MEM",
        vsz="VSZ",
        rss="RSS",
        tty="TTY",
        stat="STAT",
        start="START",
        time="TIME",
    )


def _clear_content_area(win: curses.window, height: int):
    """
    Clear the process list content area.
    
    Helper: Erases all lines between header and footer to prepare
    for fresh process list rendering.
    """
    for y in range(FIRST_DATA_ROW, height - FOOTER_OFFSET):
        try:
            win.move(y, 2)
            win.clrtoeol()
        except curses.error:
            pass


def _draw_header(win: curses.window, width: int, sort_mode: str):
    """
    Draw the header section.
    
    Helper: Renders column headers and horizontal separator line.
    """
    header = _format_header()
    try:
        win.addnstr(HEADER_ROW, 2, header, width - 3)
        win.hline(SEPARATOR_ROW, 2, curses.ACS_HLINE, width - 4)
    except curses.error:
        pass


def _draw_process_rows(
    win: curses.window,
    processes: List[ProcessInfo],
    selected_index: int,
    scroll_start: int,
    visible_lines: int,
    width: int,
    height: int,
):
    """
    Draw all visible process rows.
    
    Helper: Iterates through visible processes and renders each row
    with appropriate selection highlighting.
    """
    end_index = min(scroll_start + visible_lines, len(processes))

    for i, proc in enumerate(processes[scroll_start:end_index], start=scroll_start):
        y = FIRST_DATA_ROW + (i - scroll_start)
        if y < height - FOOTER_OFFSET:
            draw_process_row(win, y, proc, width, i == selected_index)


def draw_footer(
    win: curses.window,
    height: int,
    error_message: str = None,
    confirm_kill: bool = False,
    process_name: str = None
) -> None:
    """Draw the footer with available controls and optional error message."""
    try:
        # Clear the entire footer line first
        win.move(height - FOOTER_OFFSET, 2)
        win.clrtoeol()

        win.attron(curses.color_pair(COLOR_FOOTER))

        if confirm_kill and process_name:
            # Show kill confirmation prompt in warning color
            win.attron(curses.color_pair(COLOR_ERROR))
            confirm_text = f"⚠ Kill '{process_name}'? [Y]es / [N]o"
            win.addnstr(height - FOOTER_OFFSET, 2, confirm_text, win.getmaxyx()[1] - 3)
            win.attroff(curses.color_pair(COLOR_ERROR))
        elif error_message:
            # Show error message in red
            win.attron(curses.color_pair(COLOR_ERROR))
            win.addnstr(height - FOOTER_OFFSET, 2, error_message, win.getmaxyx()[1] - 3)
            win.attroff(curses.color_pair(COLOR_ERROR))
        else:
            footer_text = (
                "[↑↓/PgUp/PgDn/Home/End] Navigate  "
                "[C]PU  [M]em  [P]ID  [N]ame  [K]ill  [Q]uit"
            )
            win.addnstr(height - FOOTER_OFFSET, 2, footer_text, win.getmaxyx()[1] - 3)

        win.attroff(curses.color_pair(COLOR_FOOTER))
    except curses.error:
        pass


def draw_process_list(
    win: curses.window,
    processes: List[ProcessInfo],
    selected_index: int,
    scroll_start: int,
    sort_mode: str,
    error_message: str = None,
    confirm_kill: bool = False,
    process_name: str = None,
) -> None:
    """Render scrollable process list."""
    height, width = win.getmaxyx()

    _clear_content_area(win, height)
    draw_section_header(win, SECTION_HEADER_ROW,
                       f"Running Processes (Sort by {sort_mode.upper()})")
    _draw_header(win, width, sort_mode)

    visible_lines = height - VISIBLE_LINE_OFFSET
    _draw_process_rows(
        win, processes, selected_index, scroll_start,
        visible_lines, width, height
    )

    draw_footer(win, height, error_message, confirm_kill, process_name)


def _handle_navigation_keys(key: int, selected_index: int, num_processes: int) -> int:
    """
    Handle navigation key inputs and return new selected index.
    
    Helper: Processes arrow keys, page up/down, home/end keys and
    calculates the new selection index with bounds checking.
    """
    if key == curses.KEY_UP:
        return max(0, selected_index - 1)
    if key == curses.KEY_DOWN:
        return min(selected_index + 1, num_processes - 1)
    if key == curses.KEY_PPAGE:  # Page Up
        return max(0, selected_index - PAGE_JUMP_SIZE)
    if key == curses.KEY_NPAGE:  # Page Down
        return min(selected_index + PAGE_JUMP_SIZE, num_processes - 1)
    if key == curses.KEY_HOME:
        return 0
    if key == curses.KEY_END:
        return num_processes - 1
    return selected_index


def _handle_sort_keys(key: int) -> Optional[str]:
    """
    Handle sort key inputs and return new sort mode.
    
    Helper: Maps C/M/P/N keys to their respective sort modes
    (cpu, mem, pid, name).
    """
    if key in (ord("c"), ord("C")):
        return "cpu"
    if key in (ord("m"), ord("M")):
        return "mem"
    if key in (ord("p"), ord("P")):
        return "pid"
    if key in (ord("n"), ord("N")):
        return "name"
    return None


def _is_quit_or_nav_key(key: int) -> bool:
    """
    Check if key is a quit or navigation key.
    
    Helper: Returns True for keys that should exit the process viewer
    (Q for quit, D for dashboard, 1/3/4/5 for other pages).
    """
    return key in (
        ord("d"), ord("D"),
        ord("1"), ord("3"), ord("4"), ord("5"),
        ord("q"), ord("Q")
    )


def handle_process_input(
    key: int, selected_index: int, processes: List[ProcessInfo]
) -> Tuple[int, Optional[str], bool, Optional[int]]:
    """Handle key input for navigation, sorting, killing, and quitting."""
    new_selected = _handle_navigation_keys(key, selected_index, len(processes))
    new_sort_mode = _handle_sort_keys(key)
    kill_flag = key in (ord("k"), ord("K"))
    return_key = key if _is_quit_or_nav_key(key) else None

    return new_selected, new_sort_mode, kill_flag, return_key


def clamp_and_scroll(state: dict, visible_lines: int) -> None:
    """Clamp selected_index and adjust scroll_start in state."""
    processes = state["cached_processes"]
    state["selected_index"] = max(0, min(state["selected_index"], len(processes) - 1))

    sel = state["selected_index"]
    scroll = state["scroll_start"]

    # Adjust scroll position based on selection
    if sel < scroll:
        state["scroll_start"] = sel
    elif sel >= scroll + visible_lines:
        state["scroll_start"] = sel - visible_lines + 1
    elif sel == 0:
        state["scroll_start"] = 0
    elif sel == len(processes) - 1:
        state["scroll_start"] = max(0, sel - visible_lines + 1)


def init_process_viewer(stdscr: curses.window) -> dict:
    """Initialize curses and default state for the process viewer."""
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(INPUT_TIMEOUT)
    return {
        "selected_index": 0,
        "scroll_start": 0,
        "sort_mode": "cpu",
        "refresh_interval": REFRESH_INTERVAL,
        "last_refresh": 0.0,
        "cached_processes": [],
        "needs_refresh": True,
        "error_message": None,
        "error_time": 0.0,
        "confirm_kill": False,
        "kill_target_pid": None,
    }


def cleanup_and_exit(message: str = None):
    """
    Properly cleanup terminal and exit.
    
    Helper: Restores terminal to normal state, optionally prints a message,
    and exits the process.
    """
    try:
        curses.endwin()
    except Exception:  # pylint: disable=broad-except
        pass

    os.system('reset')

    if message:
        print(message)

    os._exit(0)  # pylint: disable=protected-access


def _kill_process(pid: int):
    """
    Attempt to kill a process, trying SIGTERM then SIGKILL.
    
    Helper: Sends SIGTERM for graceful shutdown, waits briefly, then
    sends SIGKILL if process still exists.
    """
    os.kill(pid, SIGTERM)

    time.sleep(KILL_RETRY_DELAY)
    try:
        os.kill(pid, SIG_CHECK)
        os.kill(pid, SIGKILL)
    except (ProcessLookupError, OSError):
        pass


def _handle_kill_confirmation(key: int, state: dict) -> Optional[int]:
    """
    Handle kill confirmation input. Returns quit key if applicable.
    
    Helper: Processes Y/N/ESC keys during kill confirmation mode and
    executes or cancels the kill operation.
    """
    if key in (ord('y'), ord('Y')):
        pid_to_kill = state["kill_target_pid"]
        try:
            _kill_process(pid_to_kill)
            state["needs_refresh"] = True
        except (PermissionError, ProcessLookupError) as e:
            state["error_message"] = f"Error: {str(e)}"
            state["error_time"] = time.time()
            state["needs_refresh"] = True

        state["confirm_kill"] = False
        state["kill_target_pid"] = None
        return None

    if key in (ord('n'), ord('N'), 27):  # N or ESC
        state["confirm_kill"] = False
        state["kill_target_pid"] = None
        state["needs_refresh"] = True
        return None

    return None


def _handle_kill_request(selected_proc: ProcessInfo, state: dict, current_pid: int):
    """
    Handle a kill request for the selected process.
    
    Helper: Checks if process is self or critical, requiring confirmation
    for critical processes and immediate kill for normal processes.
    """
    # Check if killing ourselves
    if selected_proc.pid in (current_pid, os.getpid()):
        return ord('q')

    # Check if critical - require confirmation
    if is_critical_process(selected_proc):
        state["confirm_kill"] = True
        state["kill_target_pid"] = selected_proc.pid
        state["needs_refresh"] = True
    else:
        # Non-critical - kill immediately
        try:
            _kill_process(selected_proc.pid)
            state["needs_refresh"] = True
        except (PermissionError, ProcessLookupError) as e:
            state["error_message"] = f"Error: {str(e)}"
            state["error_time"] = time.time()
            state["needs_refresh"] = True

    return None


def process_user_input(key: int, state: dict, current_pid: int) -> Optional[int]:
    """Handle user input and update state. Return key if quitting/switching, else None."""
    processes = state["cached_processes"]

    if not processes:
        return None

    # Handle kill confirmation mode
    if state.get("confirm_kill"):
        return _handle_kill_confirmation(key, state)

    sel, sort_mode, kill_flag, return_key = handle_process_input(
        key, state["selected_index"], processes
    )

    # Update selection
    if sel != state["selected_index"]:
        state["selected_index"] = sel
        state["needs_refresh"] = True

    # Update sort mode
    if sort_mode and sort_mode != state["sort_mode"]:
        state["sort_mode"] = sort_mode
        state["needs_refresh"] = True

    # Handle kill
    if kill_flag:
        quit_key = _handle_kill_request(processes[sel], state, current_pid)
        if quit_key:
            return quit_key

    return return_key


def refresh_process_state(state: dict) -> None:
    """Refresh cached processes if needed."""
    now = time.time()

    if state["needs_refresh"] or (now - state["last_refresh"] >= state["refresh_interval"]):
        state["cached_processes"] = get_all_processes(state["sort_mode"])
        state["last_refresh"] = now


def _should_clear_error(state: dict, now: float) -> bool:
    """
    Check if error message should be cleared.
    
    Helper: Returns True if error display timeout has elapsed.
    """
    if not state.get("error_message") or not state.get("error_time"):
        return False
    return (now - state["error_time"]) >= ERROR_DISPLAY_TIME


def _get_confirmation_process_name(processes: List[ProcessInfo], pid: int) -> str:
    """
    Get the process name for kill confirmation.
    
    Helper: Finds the process by PID and extracts a clean display name
    for the confirmation prompt.
    """
    for proc in processes:
        if proc.pid == pid:
            cmd = proc.command or "unknown"
            if '/' in cmd:
                cmd = cmd.split('/')[-1]
            return cmd.split()[0] if cmd else "unknown"
    return "unknown"


def _prepare_display_state(state: dict, processes: List[ProcessInfo], now: float):
    """
    Prepare display state including error messages and confirmations.
    
    Helper: Gathers current error message, confirmation status, and process
    name for rendering the footer display.
    """
    current_error = None
    if state.get("error_message") and state.get("error_time"):
        if (now - state["error_time"]) < ERROR_DISPLAY_TIME:
            current_error = state["error_message"]
        else:
            state["error_message"] = None
            state["error_time"] = 0.0

    confirm_kill = state.get("confirm_kill", False)
    process_name = None
    if confirm_kill and state.get("kill_target_pid"):
        process_name = _get_confirmation_process_name(
            processes, state["kill_target_pid"]
        )

    return current_error, confirm_kill, process_name


def _handle_window_resize(stdscr: curses.window) -> Tuple[Optional[int], Optional[int]]:
    """
    Handle terminal size and return dimensions, or None if too small.
    
    Helper: Checks terminal dimensions and displays warning if window
    is too small to display the process manager.
    """
    try:
        height, width = stdscr.getmaxyx()
    except curses.error:
        return None, None

    if height < 10 or width < 80:
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, "Terminal too small. Please resize.")
            stdscr.refresh()
        except curses.error:
            pass
        return None, None

    return height, width


def _create_or_get_window(
    stdscr: curses.window,
    nav_items: list,
    active_page: str,
    win: Optional[curses.window],
    last_dimensions: Optional[Tuple[int, int]],
    current_dimensions: Tuple[int, int]
) -> Tuple[Optional[curses.window], Optional[Tuple[int, int]]]:
    """
    Create or reuse content window based on dimension changes.
    
    Helper: Creates a new content window only when dimensions change,
    otherwise reuses existing window for efficiency.
    """
    if win is None or last_dimensions != current_dimensions:
        win = draw_content_window(stdscr, "Process Manager", nav_items, active_page)
        if win is None:
            return None, last_dimensions
        return win, current_dimensions
    return win, last_dimensions


def _initialize_render_state(stdscr: curses.window) -> dict:
    """
    Initialize the rendering state for the main loop.
    
    Helper: Sets up initial state including viewer state, window tracking,
    and timing variables needed for the render loop.
    """
    state = init_process_viewer(stdscr)
    current_pid = os.getpid()
    
    return {
        "viewer_state": state,
        "current_pid": current_pid,
        "win": None,
        "last_dimensions": None,
        "last_draw_time": 0.0,
    }


def _handle_empty_window(stdscr: curses.window) -> Optional[int]:
    """
    Handle case when content window creation fails.
    
    Helper: Checks for global key input and returns appropriate key code,
    or None if should continue loop.
    """
    key = handle_input(stdscr, GLOBAL_KEYS)
    if key != -1:
        return key
    time.sleep(0.05)
    return None


def _display_empty_process_list(win: curses.window, win_height: int):
    """
    Display message when no processes are found.
    
    Helper: Clears content area and shows "No processes found" message.
    """
    try:
        _clear_content_area(win, win_height)
        win.addstr(FIRST_DATA_ROW, 2, "No processes found.")
        win.refresh()
    except curses.error:
        pass


def _should_redraw(now: float, last_draw_time: float, needs_refresh: bool) -> bool:
    """
    Determine if screen should be redrawn.
    
    Helper: Checks if enough time has passed or if a forced refresh is needed.
    """
    return (now - last_draw_time) >= DRAW_INTERVAL or needs_refresh


def _perform_draw(
    win: curses.window,
    processes: List[ProcessInfo],
    state: dict,
    current_error: str,
    confirm_kill: bool,
    process_name: str,
):
    """
    Execute the screen drawing operations.
    
    Helper: Draws the process list and refreshes the display.
    """
    draw_process_list(
        win,
        processes,
        state["selected_index"],
        state["scroll_start"],
        state["sort_mode"],
        current_error,
        confirm_kill,
        process_name,
    )
    try:
        win.noutrefresh()
        curses.doupdate()
    except curses.error:
        pass


def _handle_resize_key(render_state: dict):
    """
    Handle terminal resize event.
    
    Helper: Resets window state to force recreation on next iteration.
    """
    render_state["win"] = None
    render_state["last_dimensions"] = None
    render_state["viewer_state"]["needs_refresh"] = True


def _process_input_key(
    key: int, viewer_state: dict, current_pid: int, render_state: dict
) -> Optional[int]:
    """
    Process user input and update state accordingly.
    
    Helper: Handles resize events and user input, returns quit key if applicable.
    """
    if key == curses.KEY_RESIZE:
        _handle_resize_key(render_state)
        return None
    
    quit_key = process_user_input(key, viewer_state, current_pid)
    
    if quit_key is not None:
        return quit_key
    
    viewer_state["needs_refresh"] = True
    return None


def _handle_main_loop_iteration(
    stdscr: curses.window,
    nav_items: list,
    active_page: str,
    render_state: dict,
) -> Optional[int]:
    """
    Execute one iteration of the main render loop.
    
    Helper: Handles window management, process display, and input processing
    for a single loop iteration.
    """
    viewer_state = render_state["viewer_state"]
    
    # Handle terminal size
    dimensions = _handle_window_resize(stdscr)
    if dimensions == (None, None):
        time.sleep(0.5)
        return None
    
    # Get or create window
    render_state["win"], render_state["last_dimensions"] = _create_or_get_window(
        stdscr, nav_items, active_page,
        render_state["win"], render_state["last_dimensions"], dimensions
    )
    
    if render_state["win"] is None:
        return _handle_empty_window(stdscr)
    
    # Get window dimensions
    try:
        win_height, win_width = render_state["win"].getmaxyx()
    except curses.error:
        render_state["win"] = None
        return None
    
    visible_lines = win_height - VISIBLE_LINE_OFFSET
    
    # Refresh process data
    refresh_process_state(viewer_state)
    processes = viewer_state["cached_processes"]
    
    # Handle empty process list
    if not processes:
        _display_empty_process_list(render_state["win"], win_height)
        time.sleep(0.1)
        return None
    
    # Update scroll position
    clamp_and_scroll(viewer_state, visible_lines)
    
    # Prepare display state
    now = time.time()
    current_error, confirm_kill, process_name = _prepare_display_state(
        viewer_state, processes, now
    )
    
    # Check if should redraw
    if _should_redraw(now, render_state["last_draw_time"], viewer_state["needs_refresh"]):
        _perform_draw(
            render_state["win"], processes, viewer_state,
            current_error, confirm_kill, process_name
        )
        render_state["last_draw_time"] = now
        viewer_state["needs_refresh"] = False
    
    # Handle input
    key = stdscr.getch()
    
    if key != -1:
        return _process_input_key(
            key, viewer_state, render_state["current_pid"], render_state
        )
    
    return None


def render_processes(
    stdscr: curses.window, nav_items: list[tuple[str, str, str]], active_page: str
) -> int:
    """Interactive curses process viewer with sorting, scrolling, and kill."""
    render_state = _initialize_render_state(stdscr)
    
    while True:
        quit_key = _handle_main_loop_iteration(
            stdscr, nav_items, active_page, render_state
        )
        
        if quit_key is not None:
            return quit_key
