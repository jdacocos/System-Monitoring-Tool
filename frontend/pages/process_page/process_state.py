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
    KEY_ESCAPE,
    KEY_ENTER,
    KEY_BACKSPACE,
    KEY_BACKSPACE_ALT1,
    KEY_BACKSPACE_ALT2,
    MAX_NICE_INPUT_LENGTH,
)
from frontend.pages.process_page.process_operations import (
    get_all_processes,
    is_critical_process,
    kill_process,
    pause_process,
    resume_process,
    get_process_display_name,
    is_process_stopped,
    set_process_priority,
    get_process_priority,
    is_zombie_process,
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
        "renice_mode": False,
        "renice_pid": None,
        "renice_input": "",
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

    # Check for renice mode
    if state.get("renice_mode"):
        display_state.renice_mode = True
        display_state.renice_pid = state.get("renice_pid")
        display_state.renice_input = state.get("renice_input", "")

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

    # Check if zombie
    if is_zombie_process(selected_proc):
        proc_name = get_process_display_name(selected_proc)
        set_error_message(state, f"Cannot pause zombie '{proc_name}' (already dead)")
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

    # Check if zombie
    if is_zombie_process(selected_proc):
        proc_name = get_process_display_name(selected_proc)
        set_error_message(state, f"Cannot resume zombie '{proc_name}' (already dead)")
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

    # Check if zombie
    if is_zombie_process(selected_proc):
        proc_name = get_process_display_name(selected_proc)
        # Simplified message without PPID:
        set_error_message(
            state,
            f"Cannot kill zombie '{proc_name}' (already dead, kill parent to reap)",
        )
        return None

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


def handle_renice_request(selected_proc: ProcessInfo, state: dict):
    """
    Handle a renice request for the selected process.
    Enters renice input mode.
    """
    # Check if zombie
    if is_zombie_process(selected_proc):
        proc_name = get_process_display_name(selected_proc)
        set_error_message(state, f"Cannot renice zombie '{proc_name}' (already dead)")
        return

    # Enter renice mode
    state["renice_mode"] = True
    state["renice_pid"] = selected_proc.pid
    state["renice_input"] = ""
    state["needs_refresh"] = True


def _try_renice_process(pid: int, nice_value: int, state: dict) -> None:
    """
    Attempt to renice a process with proper error handling.
    Updates state with success or error messages.
    """
    try:
        current_nice = get_process_priority(pid)

        # Check if trying to lower nice value without sudo
        if nice_value < current_nice and os.geteuid() != 0:
            set_error_message(
                state,
                f"Cannot lower nice from {current_nice} to {nice_value} (need sudo)",
            )
            return

        # Find process name for success message
        proc_name = "Unknown"
        for proc in state["cached_processes"]:
            if proc.pid == pid:
                proc_name = get_process_display_name(proc)
                break

        set_process_priority(pid, nice_value)
        set_success_message(
            state, f"Set nice value of '{proc_name}' (PID {pid}) to {nice_value}"
        )

    except PermissionError:
        if nice_value < 0:
            set_error_message(
                state, f"Need sudo to set negative nice values (tried: {nice_value})"
            )
        else:
            set_error_message(state, "Permission denied")
    except ProcessLookupError as e:
        set_error_message(state, f"Error: {str(e)}")


def _cancel_renice_mode(state: dict) -> None:
    """
    Cancel renice mode and reset related state.
    Clears renice mode flag, target PID, and input buffer.
    """
    state["renice_mode"] = False
    state["renice_pid"] = None
    state["renice_input"] = ""
    state["needs_refresh"] = True


def _confirm_renice(state: dict) -> None:
    """
    Process renice confirmation when Enter is pressed.
    Validates input, attempts to renice the process, and exits renice mode.
    """
    if not state["renice_input"]:
        set_error_message(state, "No nice value entered")
    else:
        try:
            nice_value = int(state["renice_input"])
            pid = state["renice_pid"]
            _try_renice_process(pid, nice_value, state)
        except ValueError:
            set_error_message(state, f"Invalid nice value: '{state['renice_input']}'")

    _cancel_renice_mode(state)


def _handle_renice_backspace(state: dict) -> None:
    """
    Handle backspace key in renice mode.
    Removes the last character from the input buffer.
    """
    state["renice_input"] = state["renice_input"][:-1]
    state["needs_refresh"] = True


def _is_valid_nice_input_char(char: str, current_input: str) -> bool:
    """
    Check if a character is valid for nice value input.

    Parameters:
        char: The character to validate
        current_input: The current input buffer

    Returns:
        True if the character is valid, False otherwise
    """
    # Only allow minus at the start
    if char == "-" and len(current_input) > 0:
        return False

    # Allow minus, plus, or digits
    return char in ("-", "+") or char.isdigit()


def _handle_renice_character_input(key: int, state: dict) -> None:
    """
    Handle character input for nice value.
    Accepts numeric characters and minus sign with validation.

    Args:
        key: The key code pressed
        state: Current state dictionary
    """
    if key in (ord("-"), ord("+")) or (ord("0") <= key <= ord("9")):
        char = chr(key)

        if not _is_valid_nice_input_char(char, state["renice_input"]):
            return

        # Limit input length
        if len(state["renice_input"]) < MAX_NICE_INPUT_LENGTH:
            state["renice_input"] += char
            state["needs_refresh"] = True


def handle_renice_input(key: int, state: dict) -> None:
    """
    Handle input during renice mode.

    Processes keyboard input for entering nice values (-20 to 19).
    Supports:
    - ESC: Cancel renice mode
    - Enter: Confirm and apply nice value
    - Backspace: Delete last character
    - Numeric input: Build nice value string

    Args:
        key: The key code from curses getch()
        state: Current state dictionary containing renice mode data
    """
    if key == KEY_ESCAPE:
        _cancel_renice_mode(state)
        return

    if key == KEY_ENTER:
        _confirm_renice(state)
        return

    # Check all backspace variants
    if key in (KEY_BACKSPACE, KEY_BACKSPACE_ALT1, KEY_BACKSPACE_ALT2):
        _handle_renice_backspace(state)
        return

    _handle_renice_character_input(key, state)


def process_user_input(key: int, state: dict, current_pid: int) -> Optional[int]:
    """
    Handle user input and update state.
    Returns key if quitting/switching pages, else None.
    """

    processes = state["cached_processes"]

    if not processes:
        return None

    # Handle renice input mode (highest priority)
    if state.get("renice_mode"):
        handle_renice_input(key, state)
        return None

    # Handle kill confirmation mode
    if state.get("confirm_kill"):
        return handle_kill_confirmation(key, state)

    sel, sort_mode, kill_flag, pause_flag, resume_flag, renice_flag, return_key = (
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

    # Handle renice
    if renice_flag:
        handle_renice_request(processes[sel], state)

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
