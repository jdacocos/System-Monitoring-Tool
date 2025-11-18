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

