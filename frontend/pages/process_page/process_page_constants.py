"""
pages/process_page/process_page_constants.py

Constants and configuration values for the process manager page.

This module centralizes all magic numbers, configuration parameters,
and constant values used throughout the process management interface.

Categories:
- Column width specifications for the process table display
- Sort key mappings for different sorting modes
- Critical process identifiers for kill protection
- Timing intervals for refresh and display updates
- OS signal numbers for process management
- UI positioning and layout constants
- Color pair assignments for different UI states
"""

# Column widths for process table display
COL_WIDTHS = {
    "user": 16,
    "pid": 6,
    "cpu": 6,
    "mem": 6,
    "vsz": 10,
    "rss": 10,
    "tty": 8,
    "stat": 6,
    "nice": 5,
    "start": 8,
    "time": 10,
    "command": 0,  # dynamic width
}

# Sort key mappings from mode name to ProcessInfo attribute
SORT_KEYS = {
    "cpu": "cpu_percent",
    "mem": "mem_percent",
    "pid": "pid",
    "name": "command",
    "nice": "nice",
}

# Critical processes that require confirmation before killing
# These are typically shells, SSH connections, and system processes
CRITICAL_PROCESSES = {
    "bash",
    "sh",
    "zsh",
    "fish",
    "tcsh",
    "csh",  # Shells
    "sshd",
    "ssh",  # SSH
    "systemd",
    "init",  # Init systems
    "systemd-logind",
    "login",  # Login managers
    "gnome-session",
    "kde-session",
    "xfce4-session",  # Desktop sessions
}

# Timing intervals (in seconds)
REFRESH_INTERVAL = 2.0  # Seconds between process data updates
DRAW_INTERVAL = 0.1  # Seconds between screen redraws (100ms)
ERROR_DISPLAY_TIME = 2.0  # Seconds to show error messages
KILL_RETRY_DELAY = 0.1  # Seconds to wait before SIGKILL after SIGTERM

# Input configuration (in milliseconds)
INPUT_TIMEOUT = 10  # Milliseconds for getch timeout

# Navigation constants
PAGE_JUMP_SIZE = 10  # Number of processes to jump with PgUp/PgDn

# OS signal numbers
SIGTERM = 15  # Graceful termination signal
SIGKILL = 9  # Force kill signal
SIG_CHECK = 0  # Check if process exists (no signal sent)

# UI positioning and layout
HEADER_ROW = 2  # Row for column headers
SEPARATOR_ROW = 3  # Row for horizontal separator line
FIRST_DATA_ROW = 4  # First row for process data
SECTION_HEADER_ROW = 1  # Row for section title
FOOTER_OFFSET = 2  # Rows from bottom for footer
VISIBLE_LINE_OFFSET = 6  # Total rows used by headers and footer

# Color pair assignments (must match color pairs initialized in ui_helpers)
COLOR_ERROR = 1  # Red/error color for warnings and errors
COLOR_FOOTER = 2  # Color for footer text
COLOR_WARNING = 3  # Yellow/warning color for critical processes
COLOR_NORMAL = 5  # Normal color for regular processes
COLOR_SELECTED = 6  # Color for selected row
