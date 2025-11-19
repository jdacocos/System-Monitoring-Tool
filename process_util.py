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

def get_process_user(pid: int) -> str | None:
    """
    Returns the username owning the process.
    Only uses os module.
    """

    proc_path = f"/proc/{pid}"

    try:
        stat_info = os.stat(proc_path)
    except FileNotFoundError:
        return None

    uid = stat_info.st_uid

    
