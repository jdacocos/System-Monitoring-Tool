"""
file_helper.py

This module provides low-level helper functions for safely reading files on
Linux systems, including virtual files in /proc. It uses os.open and os.read
to support direct, unbuffered access and avoid issues with null bytes or
non-standard file behaviors commonly found in kernel-generated files.

The helpers return decoded text or structured representations (such as lists of
lines or space-normalized command lines) while gracefully handling read errors
by returning None instead of raising exceptions.
"""

import os

DEFAULT_BUFFER = 4096
ENCODING = "utf-8"


def read_file(path: str) -> str | None:
    """
    Low-level file read helper using os.open and os.read.
    Reads the entire file in chunks and returns a decoded string,
    or None if the file cannot be read.

    Suitable for reading /proc filesystem entries.
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
    Read file using read_file() and return a list of lines.
    Equivalent to str.splitlines(), returns None if file can't be read.
    """
    result = None
    data = read_file(path)

    if data is not None:
        result = data.splitlines()

    return result


def read_cmdline(path: str) -> str | None:
    """
    Reads /proc/<pid>/cmdline which uses null ('\0') separators.
    Converts null bytes into spaces to produce a readable command line.
    Returns None if the file cannot be read.
    """
    result = None
    data = read_file(path)

    if data is not None:
        result = data.replace("\0", " ").strip()

    return result
