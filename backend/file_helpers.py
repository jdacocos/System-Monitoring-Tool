"""
file_helper.py

Provides low-level helper functions for safely reading files on Linux systems,
including virtual files in /proc.

Shows:
- Direct unbuffered file access using os.open and os.read
- Graceful handling of read errors by returning None
- Conversion of raw file contents into decoded strings, lines, or command lines

Integrates with system monitoring utilities to:
- Safely read /proc files containing process and memory info
- Normalize command lines from null-separated strings
- Provide structured or human-readable data without exceptions
"""

import os

DEFAULT_BUFFER = 4096
ENCODING = "utf-8"


def read_file(path: str) -> str | None:
    """
    Reads a file in low-level unbuffered mode and returns its contents as a string.

    Args:
        path (str): Path to the file to read.

    Returns:
        str | None: Decoded file contents as a string, or None if the file cannot be read.
    
    Notes:
        Suitable for reading /proc filesystem entries that may contain null bytes
        or non-standard behaviors.
    """
    result = None

    try:
        fd = os.open(path, os.O_RDONLY)
        chunks = []

        while True:
            data = os.read(fd, DEFAULT_BUFFER)
            if not data:
                break
            chunks.append(data)

        os.close(fd)

        result = b"".join(chunks).decode(ENCODING, errors="replace")

    except OSError:
        result = None

    return result


def read_lines(path: str) -> list[str] | None:
     """
    Reads a file and returns its contents as a list of lines.

    Args:
        path (str): Path to the file to read.

    Returns:
        list[str] | None: List of lines if the file is readable, otherwise None.
    
    Notes:
        Uses read_file() internally and applies str.splitlines().
    """
     
    result = None
    data = read_file(path)

    if data is not None:
        result = data.splitlines()

    return result


def read_cmdline(path: str) -> str | None:
    """
    Reads /proc/<pid>/cmdline and converts null-separated bytes into a readable string.

    Args:
        path (str): Path to the cmdline file.

    Returns:
        str | None: Command line with null bytes replaced by spaces,
                    or None if the file cannot be read.
    """
    
    result = None
    data = read_file(path)

    if data is not None:
        result = data.replace("\0", " ").strip()

    return result
