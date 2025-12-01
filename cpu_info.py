# Get CPU information

import time
from utilities import read_file
from collections import namedtuple

cpufreq = namedtuple("cpufreq", ["current", "min", "max"])

# ==================== CPU Counts ==================== #


# --------------------------------------------------
# Replicates psutil.cpu_count(logical=True).
# --------------------------------------------------
def get_logical_cpu_count():
    cpuinfo = read_file("/proc/cpuinfo")
    if not cpuinfo:
        return None
    return sum(1 for line in cpuinfo.splitlines() if line.startswith("processor"))


# --------------------------------------------------
# Replicates psutil.cpu_count(logical=False) by counting unique
# (physical id, core id) pairs.
# --------------------------------------------------
def get_physical_cpu_count():
    phys_core_pairs = set()
    phys_id = None
    core_id = None

    cpuinfo = read_file("/proc/cpuinfo")

    for line in cpuinfo.splitlines():
        if line.startswith("physical id"):
            phys_id = int(line.split(":")[1])
        elif line.startswith("core id"):
            core_id = int(line.split(":")[1])
            phys_core_pairs.add((phys_id, core_id))
            phys_id = None
            core_id = None

    return len(phys_core_pairs) if phys_core_pairs else None


# ==================== CPU Frequency ==================== #


# --------------------------------------------------
# Replicates psutil.cpu_freq()
# Returns a dict {current, min, max} or None.
# --------------------------------------------------
def get_cpu_freq():
    cpuinfo = read_file("/proc/cpuinfo")

    if cpuinfo is None:
        return None

    curr = None
    for line in cpuinfo.split("\n"):
        if "cpu MHz" in line:
            try:
                curr = float(line.split(":")[1].strip())
            except:
                curr = None
            break

    if curr is None:
        return None

    return cpufreq(current=curr, min=0.0, max=0.0)


# ==================== CPU Percent Per Core ==================== #


def read_proc_stat():
    data = read_file("/proc/stat")
    return [line for line in data.splitlines() if line.startswith("cpu")]


def parse_cpu_line(line):
    parts = line.split()
    return list(map(int, parts[1:]))


# --------------------------------------------------
# Returns per-core (total_time, idle_time)
# --------------------------------------------------
def cpu_totals():
    lines = read_proc_stat()
    core_lines = [l for l in lines if l.startswith("cpu") and not l.startswith("cpu ")]

    totals = []
    for line in core_lines:
        values = parse_cpu_line(line)
        idle = values[3]
        iowait = values[4]
        total_idle = idle + iowait
        total = sum(values)
        totals.append((total, total_idle))

    return totals


# --------------------------------------------------
# Replicates psutil.cpu_percent(percpu=True)
# --------------------------------------------------
def get_cpu_percent_per_core(interval=0.1):
    before = cpu_totals()
    time.sleep(interval)
    after = cpu_totals()

    percentages = []
    for (tot1, idle1), (tot2, idle2) in zip(before, after):
        total_delta = tot2 - tot1
        idle_delta = idle2 - idle1

        if total_delta <= 0:
            percentages.append(0.0)
        else:
            pct = 100.0 * (1 - idle_delta / total_delta)
            percentages.append(round(pct, 1))

    return percentages


# ==================== Test Composite ==================== #


def get_cpu_stats() -> dict:
    per_core = get_cpu_percent_per_core(interval=0.1)
    overall = sum(per_core) / len(per_core) if per_core else 0.0

    return {
        "overall": overall,
        "per_core": per_core,
        "freq": get_cpu_freq(),
        "logical": get_logical_cpu_count(),
        "physical": get_physical_cpu_count(),
    }
