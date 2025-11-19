from process_struct import ProcessInfo


import os
from typing import Iterator

LNX_FS = '/proc'

def open_file_system(path=LNX_FS) -> Iterator[os.DirEntry]:
    """
    Open a directory iterator to the /proc file system.
    """
    
    try:
        return os.scandir(path)
    except FileNotFoundError:
        print(f"Unable to open {path}")
        
def get_process_pids() -> list[int] :
    """
    Retrieves all pids from /proc
    """
    
    pids = []
    with open_file_system() as entries:
        for entry in entries:
            if entry.name.isdigit():
                pids.append(int(entry.name))

    return pids

def _uid_to_username(uid: int) -> str | None:
    """
    Helper: Convert a UID to a username using system password.
    Returns None if UID is not found.
    """
    username = None
    
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.strip().split(":")

                if len(parts) < 3:
                    continue

                try:
                    entry_uid = int(parts[2])
                except ValueError:
                    continue

                if entry_uid == uid:
                    username = parts[0]
                    break
    except (FileNotFoundError, PermissionError):
        pass

    return username
                
def get_process_user(pid: int) -> str | None:
    """
    Returns the username owning the process.
    Only uses os module.
    """

    proc_path = f"/proc/{pid}"
    username = None

    
    try:
        stat_info = os.stat(proc_path)
        uid = stat_info.st_uid
        username = _uid_to_username(uid)
    except FileNotFoundError:
        pass

    return username
    
