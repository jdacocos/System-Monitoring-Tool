
import os

def read_file(path):
    fd = os.open(path, os.O_RDONLY)

    #python handles buffer unlike in C
    data = os.read(fd, 4096).decode()
    os.close(fd)
    return data
