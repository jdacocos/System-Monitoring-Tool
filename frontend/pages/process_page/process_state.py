"""
pages/process_page/process_state.py

State management for the process manager.
Handles viewer state, message display, and process operations.
"""

import curses
import os
import time
from typing import List, Optional

from frontend.utils.ui_helpers import init_colors
from frontend.pages.process_page.process_page_constants import (
    REFRESH_INTERVAL,
    INPUT_TIMEOUT,
    ERROR_DISPLAY_TIME,
)
from frontend.pages.process_page.process_operations import (
    get_all_processes,
    is_critical_process,
    kill_process,
    pause_process,
    resume_process,
    get_process_display_name,
    is_process_stopped,
)
from frontend.pages.process_page.process_display import DisplayState
from frontend.pages.process_page.process_input import handle_process_input
from backend.process_struct import ProcessInfo


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
        "success_message": None,
        "success_time": 0.0,
        "confirm_kill": False,
        "kill_target_pid": None,
    }


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


def set_error_message(state: dict, message: str):
    """Helper to set error message and timestamp."""
    state["error_message"] = message
    state["error_time"] = time.time()
    state["needs_refresh"] = True


def set_success_message(state: dict, message: str):
    """Helper to set success message and timestamp."""
    state["success_message"] = message
    state["success_time"] = time.time()
    state["needs_refresh"] = True


def refresh_process_state(state: dict) -> None:
    """Refresh cached processes if needed."""
    now = time.time()

    if state["needs_refresh"] or (
        now - state["last_refresh"] >= state["refresh_interval"]
    ):
        state["cached_processes"] = get_all_processes(state["sort_mode"])
        state["last_refresh"] = now


def build_display_state(
    state: dict, processes: List[ProcessInfo], now: float
) -> DisplayState:
    """
    Build display state including error messages, success messages, and confirmations.
    """
    display_state = DisplayState()

    # Check for error message
    if state.get("error_message") and state.get("error_time"):
        if (now - state["error_time"]) < ERROR_DISPLAY_TIME:
            display_state.error_message = state["error_message"]
        else:
            state["error_message"] = None
            state["error_time"] = 0.0

    # Check for success message
    if state.get("success_message") and state.get("success_time"):
        if (now - state["success_time"]) < ERROR_DISPLAY_TIME:
            display_state.success_message = state["success_message"]
        else:
            state["success_message"] = None
            state["success_time"] = 0.0

    # Check for kill confirmation
    display_state.confirm_kill = state.get("confirm_kill", False)
    if display_state.confirm_kill and state.get("kill_target_pid"):
        # Find the process and get its name
        for proc in processes:
            if proc.pid == state["kill_target_pid"]:
                display_state.process_name = get_process_display_name(proc)
                break

    return display_state


def handle_kill_confirmation(key: int, state: dict) -> None:
    """
    Handle kill confirmation input.
    Processes Y/N/ESC keys during kill confirmation mode and
    executes or cancels the kill operation.
    """
    if key in (ord("y"), ord("Y")):
        pid_to_kill = state["kill_target_pid"]
        try:
            kill_process(pid_to_kill)
            state["needs_refresh"] = True
        except (PermissionError, ProcessLookupError) as e:
            set_error_message(state, f"Error: {str(e)}")

        state["confirm_kill"] = False
        state["kill_target_pid"] = None

    elif key in (ord("n"), ord("N"), 27):  # N or ESC
        state["confirm_kill"] = False
        state["kill_target_pid"] = None
        state["needs_refresh"] = True


def handle_pause_request(selected_proc: ProcessInfo, state: dict, current_pid: int):
    """
    Handle a pause request for the selected process.
    Checks if process can be paused and sends SIGSTOP.
    """
    # Check if trying to pause ourselves
    if selected_proc.pid in (current_pid, os.getpid()):
        set_error_message(state, "Cannot pause own process")
        return

    # Check if process is already stopped
    if is_process_stopped(selected_proc):
        set_error_message(
            state,
            f"Process '{get_process_display_name(selected_proc)}' is already stopped",
        )
        return

    # Check if critical
    if is_critical_process(selected_proc):
        set_error_message(state, "Cannot pause critical process")
        return

    # Try to pause
    try:
        pause_process(selected_proc.pid)
        set_success_message(
            state,
            f"Paused '{get_process_display_name(selected_proc)}' (PID {selected_proc.pid})",
        )
    except (PermissionError, ProcessLookupError) as e:
        set_error_message(state, f"Error: {str(e)}")


def handle_resume_request(selected_proc: ProcessInfo, state: dict, current_pid: int):
    """
    Handle a resume request for the selected process.
    Checks if process is stopped and sends SIGCONT.
    """
    # Check if trying to resume ourselves (shouldn't happen but be safe)
    if selected_proc.pid in (current_pid, os.getpid()):
        set_error_message(state, "Cannot resume own process")
        return

    # Check if process is actually stopped
    if not is_process_stopped(selected_proc):
        set_error_message(
            state,
            f"Process '{get_process_display_name(selected_proc)}' is not stopped",
        )
        return

    # Try to resume
    try:
        resume_process(selected_proc.pid)
        set_success_message(
            state,
            f"Resumed '{get_process_display_name(selected_proc)}' (PID {selected_proc.pid})",
        )
    except (PermissionError, ProcessLookupError) as e:
        set_error_message(state, f"Error: {str(e)}")


def handle_kill_request(selected_proc: ProcessInfo, state: dict, current_pid: int):
    """
    Handle a kill request for the selected process.
    Checks if process is self or critical, requiring confirmation
    for critical processes and immediate kill for normal processes.
    """
    # Check if killing ourselves
    if selected_proc.pid in (current_pid, os.getpid()):
        return ord("q")

    # Check if critical - require confirmation
    if is_critical_process(selected_proc):
        state["confirm_kill"] = True
        state["kill_target_pid"] = selected_proc.pid
        state["needs_refresh"] = True
    else:
        # Non-critical - kill immediately
        try:
            kill_process(selected_proc.pid)
            state["needs_refresh"] = True
        except (PermissionError, ProcessLookupError) as e:
            set_error_message(state, f"Error: {str(e)}")

    return None


def process_user_input(key: int, state: dict, current_pid: int) -> Optional[int]:
    """
    Handle user input and update state.
    Returns key if quitting/switching pages, else None.
    """

    processes = state["cached_processes"]

    if not processes:
        return None

    # Handle kill confirmation mode
    if state.get("confirm_kill"):
        return handle_kill_confirmation(key, state)

    sel, sort_mode, kill_flag, pause_flag, resume_flag, return_key = (
        handle_process_input(key, state["selected_index"], processes)
    )

    # Update selection
    if sel != state["selected_index"]:
        state["selected_index"] = sel
        state["needs_refresh"] = True

    # Update sort mode
    if sort_mode and sort_mode != state["sort_mode"]:
        state["sort_mode"] = sort_mode
        state["needs_refresh"] = True

    # Handle pause
    if pause_flag:
        handle_pause_request(processes[sel], state, current_pid)

    # Handle resume
    if resume_flag:
        handle_resume_request(processes[sel], state, current_pid)

    # Handle kill
    if kill_flag:
        quit_key = handle_kill_request(processes[sel], state, current_pid)
        if quit_key:
            return quit_key

    return return_key


def cleanup_and_exit(message: str = None):
    """
    Properly cleanup terminal and exit.
    Restores terminal to normal state, optionally prints a message,
    and exits the process.
    """
    try:
        curses.endwin()
    except curses.error:
        pass

    os.system("reset")

    if message:
        print(message)

    os._exit(0)
