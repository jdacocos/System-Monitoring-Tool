# File to test modules independently

import psutil

from cpu import get_cpu_usage
from memory import get_mem_usage

#-------------------------------------------------------------
# CPU TESTING
#-------------------------------------------------------------

print("\n========== CPU USAGE COMPARISON ==========\n")

# --- Per-core CPU % --- #

print("psutil per-core CPU %:")
psutil_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
print(psutil_per_core)

# --- Overall CPU % --- #

psutil_overall = psutil.cpu_percent(interval=0.1)

print("\n---------- CPU Total Usage ----------\n")
print("psutil overall CPU:", psutil_overall, "%")


# --- CPU FREQUENCY --- #
print("\n========== CPU FREQUENCY ==========\n")
print("psutil:", psutil.cpu_freq())


# --- CPU COUNTS ---
print("\n========== CPU COUNTS ==========\n")
print("psutil logical:", psutil.cpu_count(logical=True))

print()
print("psutil physical:", psutil.cpu_count(logical=False))


# --- Full stats dict ---
print("\n========== FULL STATS ==========\n")

print("\npsutil reference:")
print({
    "overall": psutil_overall,
    "per_core": psutil_per_core,
    "freq": psutil.cpu_freq(),
    "logical": psutil.cpu_count(logical=True),
    "physical": psutil.cpu_count(logical=False),
})

print("\n========================================\n")


#-------------------------------------------------------------
#-------------------------------------------------------------

# MEMORY TESTING

print("---------- Memory Usage ----------")

print()
print("Memory: ", get_mem_usage())

print()

vm = psutil.virtual_memory()
print("psutil Total:", vm.total)
print("psutil Used:", vm.used)
print("psutil Available:", vm.available)
print("psutil Percent:", vm.percent, "%")
print()
