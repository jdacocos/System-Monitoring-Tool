"""
process_display.py

Display and rendering functions for the Process Manager UI.

Shows:
- Scrollable process list with selection highlighting
- Colored process rows for normal, critical, and selected processes
- Headers, separators, and aligned column formatting
- Footer messages for renice input, kill confirmation, errors, and success
- Default navigation and action help text

Integrates with the generic UI page loop to handle:
- Window rendering
- Keyboard input
- Screen refreshes

Dependencies:
- curses (for terminal rendering)
- dataclasses (for DisplayState and DrawParams)
- typing.List
- frontend.utils.ui_helpers (draw_section_header)
- frontend.pages.process_page.process_page_constants
- frontend.pages.process_page.process_operations
- backend.process_struct (ProcessInfo)
"""

import curses
from typing import List
from dataclasses import dataclass

from frontend.utils.ui_helpers import draw_section_header
from frontend.pages.process_page.process_page_constants import (
    COL_WIDTHS,
    PROCESS_HEADER_TEMPLATE,
    PROCESS_ROW_TEMPLATE,
    HEADER_ROW,
    SEPARATOR_ROW,
    FIRST_DATA_ROW,
    SECTION_HEADER_ROW,
    FOOTER_OFFSET,
    FOOTER_TEXT,
    FOOTER_CONFIRM_KILL_TEMPLATE,
    VISIBLE_LINE_OFFSET,
    COLOR_ERROR,
    COLOR_FOOTER,
    COLOR_WARNING,
    COLOR_NORMAL,
    COLOR_SELECTED,
)
from frontend.pages.process_page.process_operations import is_critical_process
from backend.process_struct import ProcessInfo


@dataclass
class DisplayState:
    """State for display messages and confirmations."""

    error_message: str = None
    success_message: str = None
    confirm_kill: bool = False
    process_name: str = None
    renice_mode: bool = False
    renice_pid: int = None
    renice_input: str = ""


@dataclass
class DrawParams:
    """Parameters for drawing operations."""

    processes: List[ProcessInfo]
    selected_index: int
    scroll_start: int
    sort_mode: str


def _get_process_color(proc: ProcessInfo, is_selected: bool) -> int:
    """
    Helper:
    Determine the color pair for a process based on its state.

    Args:
        proc (ProcessInfo): The process information object.
        is_selected (bool): Whether the row is currently selected.

    Returns:
        int: Curses color pair for rendering this process row.
    """

    is_critical = is_critical_process(proc)

    if is_selected:
        return COLOR_ERROR if is_critical else COLOR_SELECTED

    return COLOR_WARNING if is_critical else COLOR_NORMAL


def _format_process_line(proc: ProcessInfo, width: int) -> str:
    """
    Helper:
    Format a process info object into a displayable row string.

    Args:
        proc (ProcessInfo): The process information object.
        width (int): Maximum width for the display line.

    Returns:
        str: Formatted process row text.
    """

    tty_display = (proc.tty or "?")[: COL_WIDTHS["tty"] - 1]

    # Calculate the available width for the command column
    fixed_width = sum(v for k, v in COL_WIDTHS.items() if k != "command")
    command_width = max(10, width - 3 - fixed_width)  # 2 left padding + 1 right border
    command_display = (proc.command or "")[:command_width]

    return (
        PROCESS_ROW_TEMPLATE.format(
            user=proc.user,
            pid=proc.pid,
            cpu=f"{proc.cpu_percent:.1f}",
            mem=f"{proc.mem_percent:.1f}",
            vsz=proc.vsz,
            rss=proc.rss,
            tty=tty_display,
            stat=proc.stat,
            nice=proc.nice,
            start=proc.start,
            time=proc.time,
            user_w=COL_WIDTHS["user"],
            pid_w=COL_WIDTHS["pid"],
            cpu_w=COL_WIDTHS["cpu"],
            mem_w=COL_WIDTHS["mem"],
            vsz_w=COL_WIDTHS["vsz"],
            rss_w=COL_WIDTHS["rss"],
            tty_w=COL_WIDTHS["tty"],
            stat_w=COL_WIDTHS["stat"],
            nice_w=COL_WIDTHS["nice"],
            start_w=COL_WIDTHS["start"],
            time_w=COL_WIDTHS["time"],
        )
        + command_display
    )


def draw_process_row(
    win: curses.window, y: int, proc: ProcessInfo, width: int, is_selected: bool
) -> None:
    """
    Draw a single process row in the given window.

    Args:
        win (curses.window): Window object to draw in.
        y (int): Y-coordinate to draw the row.
        proc (ProcessInfo): Process to display.
        width (int): Window width.
        is_selected (bool): Whether this row is selected.
    """

    line = _format_process_line(proc, width - 1)  # leave last column for │
    color_pair = _get_process_color(proc, is_selected)
    try:
        # Draw the row content with its color
        win.attron(curses.color_pair(color_pair))
        win.addnstr(y, 2, line, width - 2)
        win.attroff(curses.color_pair(color_pair))

        # Draw the right-hand border in normal color
        win.addch(y, width - 1, "│", curses.color_pair(COLOR_NORMAL))
    except curses.error:
        pass


def _format_header() -> str:
    """
    Helper:
    Format the process list header line with proper spacing and alignment.

    Uses PROCESS_HEADER_TEMPLATE and column widths from process_page_constants
    to generate a consistent header for the process table display.

    Returns:
        str: Formatted header string ready for display in the curses window.
    """

    return PROCESS_HEADER_TEMPLATE.format(
        user="USER",
        pid="PID",
        cpu="%CPU",
        mem="%MEM",
        vsz="VSZ",
        rss="RSS",
        tty="TTY",
        stat="STAT",
        nice="NI",
        start="START",
        time="TIME",
        user_w=COL_WIDTHS["user"],
        pid_w=COL_WIDTHS["pid"],
        cpu_w=COL_WIDTHS["cpu"],
        mem_w=COL_WIDTHS["mem"],
        vsz_w=COL_WIDTHS["vsz"],
        rss_w=COL_WIDTHS["rss"],
        tty_w=COL_WIDTHS["tty"],
        stat_w=COL_WIDTHS["stat"],
        nice_w=COL_WIDTHS["nice"],
        start_w=COL_WIDTHS["start"],
        time_w=COL_WIDTHS["time"],
    )


def clear_content_area(win: curses.window, height: int) -> None:
    """
    Clear all lines between the header and footer.

    Args:
        win (curses.window): Window to clear.
        height (int): Window height.
    """

    for y in range(FIRST_DATA_ROW, height - FOOTER_OFFSET):
        try:
            win.move(y, 2)
            win.clrtoeol()
        except curses.error:
            pass


def draw_header(win: curses.window, width: int) -> None:
    """
    Draw the process table header with borders and separator.

    Args:
        win (curses.window): Window to draw in.
        width (int): Window width.
    """

    header = _format_header()
    try:
        # Draw left border │
        win.addch(HEADER_ROW, 1, "│", curses.color_pair(COLOR_NORMAL))

        # Draw header text starting with 1 space padding
        win.addnstr(
            HEADER_ROW, 1, " " + header, width - 3, curses.color_pair(COLOR_NORMAL)
        )

        # Draw right border │
        win.addch(HEADER_ROW, width - 1, "│", curses.color_pair(COLOR_NORMAL))

        # Draw horizontal line under the header
        win.addch(SEPARATOR_ROW, 0, "│", curses.color_pair(COLOR_NORMAL))
        win.hline(SEPARATOR_ROW, 1, curses.ACS_HLINE, width - 3)
        win.addch(SEPARATOR_ROW, width - 1, "│", curses.color_pair(COLOR_NORMAL))

    except curses.error:
        pass


def draw_process_rows(
    win: curses.window,
    draw_params: DrawParams,
    visible_lines: int,
    height: int,
) -> None:
    """
    Draw all visible process rows in the list.

    Args:
        win (curses.window): Window to draw in.
        draw_params (DrawParams): Parameters including processes, scroll, selection, and sort.
        visible_lines (int): Number of visible lines in the window.
        height (int): Window height.
    """

    width = win.getmaxyx()[1]
    end_index = min(
        draw_params.scroll_start + visible_lines, len(draw_params.processes)
    )

    for i, proc in enumerate(
        draw_params.processes[draw_params.scroll_start : end_index],
        start=draw_params.scroll_start,
    ):
        y = FIRST_DATA_ROW + (i - draw_params.scroll_start)
        if y < height - FOOTER_OFFSET:
            draw_process_row(win, y, proc, width, i == draw_params.selected_index)


def _draw_footer_border(win: curses.window, height: int) -> None:
    """
    Helper:
    Draw the right border of the footer line.

    Parameters:
        win: The curses window to draw in
        height: Window height for calculating footer position
    """
    try:
        win.addch(
            height - FOOTER_OFFSET,
            win.getmaxyx()[1] - 1,
            "│",
            curses.color_pair(COLOR_NORMAL),
        )
    except curses.error:
        pass


def _clear_footer_line(win: curses.window, height: int) -> None:
    """
    Helper:
    Clear the footer line in preparation for new content.

    Parameters:
        win: The curses window to clear
        height: Window height for calculating footer position
    """
    try:
        win.move(height - FOOTER_OFFSET, 2)
        win.clrtoeol()
    except curses.error:
        pass


def _draw_renice_prompt(
    win: curses.window, height: int, footer_width: int, display_state: DisplayState
) -> None:
    """
    Helper:
    Draw the renice input prompt in the footer.

    Parameters:
        win: The curses window to draw in
        height: Window height for calculating footer position
        footer_width: Maximum width for footer text
        display_state: Current display state containing renice information
    """
    try:
        win.attron(curses.color_pair(COLOR_FOOTER))
        prompt = (
            f"Enter nice value for PID {display_state.renice_pid} "
            f"(-20 to 19): {display_state.renice_input}"
        )
        win.addnstr(height - FOOTER_OFFSET, 2, prompt, footer_width)
        win.attroff(curses.color_pair(COLOR_FOOTER))
    except curses.error:
        pass


def _draw_kill_confirmation(
    win: curses.window, height: int, footer_width: int, display_state: DisplayState
) -> None:
    """
    Helper:
    Draw the kill confirmation prompt in the footer.

    Parameters:
        win: The curses window to draw in
        height: Window height for calculating footer position
        footer_width: Maximum width for footer text
        display_state: Current display state containing process name
    """
    try:
        win.attron(curses.color_pair(COLOR_ERROR))
        confirm_text = FOOTER_CONFIRM_KILL_TEMPLATE.format(
            process_name=display_state.process_name
        )
        win.addnstr(height - FOOTER_OFFSET, 2, confirm_text, footer_width)
        win.attroff(curses.color_pair(COLOR_ERROR))
    except curses.error:
        pass


def _draw_error_message(
    win: curses.window, height: int, footer_width: int, message: str
) -> None:
    """
    Helper:
    Draw an error message in the footer.

    Parameters:
        win: The curses window to draw in
        height: Window height for calculating footer position
        footer_width: Maximum width for footer text
        message: The error message to display
    """
    try:
        win.attron(curses.color_pair(COLOR_ERROR))
        win.addnstr(height - FOOTER_OFFSET, 2, message, footer_width)
        win.attroff(curses.color_pair(COLOR_ERROR))
    except curses.error:
        pass


def _draw_success_message(
    win: curses.window, height: int, footer_width: int, message: str
) -> None:
    """
    Helper:
    Draw a success message in the footer.

    Parameters:
        win: The curses window to draw in
        height: Window height for calculating footer position
        footer_width: Maximum width for footer text
        message: The success message to display
    """
    try:
        win.attron(curses.color_pair(COLOR_FOOTER))
        win.addnstr(height - FOOTER_OFFSET, 2, message, footer_width)
        win.attroff(curses.color_pair(COLOR_FOOTER))
    except curses.error:
        pass


def _draw_default_footer(win: curses.window, height: int, footer_width: int) -> None:
    """
    Helper:
    Draw the default footer with navigation, sort, and action help text.

    Parameters:
        win: The curses window to draw in
        height: Window height for calculating footer position
        footer_width: Maximum width for footer text
    """
    try:
        win.attron(curses.color_pair(COLOR_FOOTER))
        win.addnstr(height - FOOTER_OFFSET, 2, FOOTER_TEXT, footer_width)
        win.attroff(curses.color_pair(COLOR_FOOTER))
    except curses.error:
        pass


def draw_footer(win: curses.window, height: int, display_state: DisplayState) -> None:
    """
    Draw the footer with context-appropriate content.

    Displays different footer content based on current state:
    - Renice input prompt when in renice mode
    - Kill confirmation when confirming kill
    - Error messages when errors occur
    - Success messages after successful operations
    - Default help text otherwise

    Parameters:
        win: The curses window to draw in
        height: Window height for calculating footer position
        display_state: Current display state determining footer content
    """
    _clear_footer_line(win, height)
    footer_width = win.getmaxyx()[1] - 3  # leave right border

    if display_state.renice_mode and display_state.renice_pid:
        _draw_renice_prompt(win, height, footer_width, display_state)
    elif display_state.confirm_kill and display_state.process_name:
        _draw_kill_confirmation(win, height, footer_width, display_state)
    elif display_state.error_message:
        _draw_error_message(win, height, footer_width, display_state.error_message)
    elif display_state.success_message:
        _draw_success_message(win, height, footer_width, display_state.success_message)
    else:
        _draw_default_footer(win, height, footer_width)

    _draw_footer_border(win, height)


def draw_process_list(
    win: curses.window, draw_params: DrawParams, display_state: DisplayState
) -> None:
    """
    Render the complete scrollable process list with header and footer.

    Args:
        win (curses.window): Window to draw in.
        draw_params (DrawParams): Parameters for visible
            processes, scroll, selection, and sort mode.
        display_state (DisplayState): Current state for footer messages and confirmations.
    """

    height, width = win.getmaxyx()

    clear_content_area(win, height)
    draw_section_header(
        win,
        SECTION_HEADER_ROW,
        f"Running Processes (Sort by {draw_params.sort_mode.upper()})",
    )
    draw_header(win, width)

    visible_lines = height - VISIBLE_LINE_OFFSET
    draw_process_rows(win, draw_params, visible_lines, height)

    draw_footer(win, height, display_state)


def display_empty_process_list(win: curses.window, win_height: int) -> None:
    """
    Display a message indicating no processes are available.

    Args:
        win (curses.window): Window to draw in.
        win_height (int): Window height for clearing content area.
    """

    try:
        clear_content_area(win, win_height)
        win.addstr(FIRST_DATA_ROW, 2, "No processes found.")
        win.refresh()
    except curses.error:
        pass


def perform_draw(
    win: curses.window, draw_params: DrawParams, display_state: DisplayState
) -> None:
    """
    Execute full screen drawing operations and refresh.

    Args:
        win (curses.window): Window to draw in.
        draw_params (DrawParams): Parameters for rendering processes.
        display_state (DisplayState): Current display state for footer and messages.
    """
    draw_process_list(win, draw_params, display_state)
    try:
        win.noutrefresh()
        curses.doupdate()
    except curses.error:
        pass
