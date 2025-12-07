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
    Format a process info into a display line.
    Ensures the line fits within the window width, leaving space for the right border.
    """
    tty_display = (proc.tty or "?")[: COL_WIDTHS["tty"] - 1]
    # Total width of all fixed columns except command
    fixed_width = sum(v for k, v in COL_WIDTHS.items() if k != "command")
    # Reserve 1 column for the right border │
    command_width = max(10, width - 3 - fixed_width)  # 2 left padding + 1 right border
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
    Format the process list header.
    Creates column headers with proper spacing and alignment.
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
    """Draw the footer with available controls and optional error/success message."""
    try:
        # Clear the entire footer line first
        win.move(height - FOOTER_OFFSET, 2)
        win.clrtoeol()

        footer_width = win.getmaxyx()[1] - 3  # leave last column for │

        if display_state.confirm_kill and display_state.process_name:
            # Show kill confirmation prompt in warning color
            win.attron(curses.color_pair(COLOR_ERROR))
            confirm_text = f"⚠ Kill '{display_state.process_name}'? [Y]es / [N]o"
            win.addnstr(height - FOOTER_OFFSET, 2, confirm_text, footer_width)
            win.attroff(curses.color_pair(COLOR_ERROR))
        elif display_state.error_message:
            # Show error message in red
            win.attron(curses.color_pair(COLOR_ERROR))
            win.addnstr(
                height - FOOTER_OFFSET, 2, display_state.error_message, footer_width
            )
            win.attroff(curses.color_pair(COLOR_ERROR))
        elif display_state.success_message:
            # Show success message in footer color
            win.attron(curses.color_pair(COLOR_FOOTER))
            win.addnstr(
                height - FOOTER_OFFSET, 2, display_state.success_message, footer_width
            )
            win.attroff(curses.color_pair(COLOR_FOOTER))
        else:
            footer_text = (
                "[↑↓/PgUp/PgDn/Home/End] Navigate  "
                "[C]PU  [M]em  [P]ID  [N]ame  [S]top  [R]esume  [K]ill  [Q]uit"
            )
            win.attron(curses.color_pair(COLOR_FOOTER))
            win.addnstr(height - FOOTER_OFFSET, 2, footer_text, footer_width)
            win.attroff(curses.color_pair(COLOR_FOOTER))

        # Draw the right-hand border in normal color
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
