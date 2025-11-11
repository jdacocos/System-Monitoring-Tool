# Get CPU information 

import time
import os

def read_file(path):
    fd = os.open(path, os.O_RDONLY)

    #python handles buffer unlike in C
    data = os.read(fd, 4096).decode()
    os.close(fd)
    return data

def get_cpu_times():
    content = read_file("/proc/stat")
    values = list(map(int, content.split("\n")[0].split()[1:]))
    idle = values[3] + values[4]
    return idle, sum(values)

def get_cpu_usage():
    idle1, total1 = get_cpu_times()
    time.sleep(0.1)
    idle2, total2 = get_cpu_times()
    return round(100 * (1 - (idle2 - idle1) / (total2 - total1)), 2)
