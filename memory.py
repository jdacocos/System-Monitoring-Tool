# Get memory usage information

from utilities import read_file

def get_mem_usage():
    mem = {}
    content = read_file("/proc/meminfo").split("\n")
    for line in content:
        if ":" in line:
            k, v = line.split(":")
            mem[k] = int(v.strip().split()[0])

    total = mem["MemTotal"]
    free = mem["MemFree"]
    buffers = mem["Buffers"]
    cached = mem["Cached"]
    used = total - (free + buffers + cached)

    return {
        "total_mb": round(total / 1024, 2),
        "used_mb": round(used / 1024, 2),
        "free_mb": round(free / 1024, 2),
        "cached_mb": round(cached / 1024, 2)
    }
