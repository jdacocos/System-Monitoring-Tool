"""
pages/process_page/process_display.py

Display and rendering functions for the process manager UI.
Handles all visual presentation of process information.
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


@dataclass
class DrawParams:
    """Parameters for drawing operations."""

    processes: List[ProcessInfo]
    selected_index: int
    scroll_start: int
    sort_mode: str


def _get_process_color(proc: ProcessInfo, is_selected: bool) -> int:
    """
    Determine the color pair for a process based on its state.
    Returns appropriate color for critical/normal processes
    and selected/unselected states.
    """
    is_critical = is_critical_process(proc)

    if is_selected:
        return COLOR_ERROR if is_critical else COLOR_SELECTED

    return COLOR_WARNING if is_critical else COLOR_NORMAL


def _format_process_line(proc: ProcessInfo, width: int) -> str:
    """
    Format a process info into a display line using PROCESS_HEADER_TEMPLATE.
    Ensures the line fits within the window width, leaving space for the right border.
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
):
    """Draw a single process row in the window."""
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
    """Format the process list header with proper spacing and alignment."""
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


def clear_content_area(win: curses.window, height: int):
    """
    Clear the process list content area.
    Erases all lines between header and footer to prepare
    for fresh process list rendering.
    """
    for y in range(FIRST_DATA_ROW, height - FOOTER_OFFSET):
        try:
            win.move(y, 2)
            win.clrtoeol()
        except curses.error:
            pass


def draw_header(win: curses.window, width: int):
    """
    Draw the header section with left and right borders and horizontal separator line.
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
):
    """
    Draw all visible process rows.
    Iterates through visible processes and renders each row
    with appropriate selection highlighting.
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


def draw_footer(win: curses.window, height: int, display_state: DisplayState) -> None:
    """Draw the footer with logical sectors: navigation, sort, actions."""
    try:
        # Clear the footer line first
        win.move(height - FOOTER_OFFSET, 2)
        win.clrtoeol()
        footer_width = win.getmaxyx()[1] - 3  # leave right border

        if display_state.confirm_kill and display_state.process_name:
            win.attron(curses.color_pair(COLOR_ERROR))
            confirm_text = FOOTER_CONFIRM_KILL_TEMPLATE.format(
                process_name=display_state.process_name
            )
            win.addnstr(height - FOOTER_OFFSET, 2, confirm_text, footer_width)
            win.attroff(curses.color_pair(COLOR_ERROR))
        elif display_state.error_message:
            win.attron(curses.color_pair(COLOR_ERROR))
            win.addnstr(
                height - FOOTER_OFFSET, 2, display_state.error_message, footer_width
            )
            win.attroff(curses.color_pair(COLOR_ERROR))
        elif display_state.success_message:
            win.attron(curses.color_pair(COLOR_FOOTER))
            win.addnstr(
                height - FOOTER_OFFSET, 2, display_state.success_message, footer_width
            )
            win.attroff(curses.color_pair(COLOR_FOOTER))
        else:
            win.attron(curses.color_pair(COLOR_FOOTER))
            win.addnstr(height - FOOTER_OFFSET, 2, FOOTER_TEXT, footer_width)
            win.attroff(curses.color_pair(COLOR_FOOTER))

        # Draw right border
        win.addch(
            height - FOOTER_OFFSET,
            win.getmaxyx()[1] - 1,
            "│",
            curses.color_pair(COLOR_NORMAL),
        )

    except curses.error:
        pass


def draw_process_list(
    win: curses.window, draw_params: DrawParams, display_state: DisplayState
) -> None:
    """Render scrollable process list."""
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


def display_empty_process_list(win: curses.window, win_height: int):
    """
    Display message when no processes are found.
    Clears content area and shows "No processes found" message.
    """
    try:
        clear_content_area(win, win_height)
        win.addstr(FIRST_DATA_ROW, 2, "No processes found.")
        win.refresh()
    except curses.error:
        pass


def perform_draw(
    win: curses.window, draw_params: DrawParams, display_state: DisplayState
):
    """
    Execute the screen drawing operations.
    Draws the process list and refreshes the display.
    """
    draw_process_list(win, draw_params, display_state)
    try:
        win.noutrefresh()
        curses.doupdate()
    except curses.error:
        pass
