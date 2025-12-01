# File to test modules independently

import psutil

from cpu_info import (
    get_cpu_percent_per_core,
    get_cpu_freq,
    get_logical_cpu_count,
    get_physical_cpu_count,
    get_cpu_stats,
)
from memory import get_mem_usage


#-------------------------------------------------------------
# CPU TESTING
#-------------------------------------------------------------

print("\n==================== CPU USAGE COMPARISON ====================\n")

# ---------- Per-core CPU % ---------- #

print("---------- Per-Core CPU% ----------\n")

print("Our per-core CPU%:")
our_per_core = get_cpu_percent_per_core(interval=0.1)
print(our_per_core)

print("psutil per-core CPU %:")
psutil_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
print(psutil_per_core)

# ---------- Overall CPU % ---------- #

print("\n---------- CPU Total Usage ----------\n")

our_overall = sum(our_per_core) / len(our_per_core) if our_per_core else 0
print("our overall CPU:", our_overall, "%")

psutil_overall = psutil.cpu_percent(interval=0.1)
print("psutil overall CPU:", psutil_overall, "%")

print("\n==============================================================\n")



print("\n==================== CPU Frequency ====================\n")

print("our Freq:", get_cpu_freq())
print("psutil:", psutil.cpu_freq())

print("\n=======================================================\n")

print("\n==================== CPU Counts ====================\n")

print("our logical:", get_logical_cpu_count())
print("our physical:", get_physical_cpu_count(), "\n")

print("psutil logical:", psutil.cpu_count(logical=True))
print("psutil physical:", psutil.cpu_count(logical=False))

print("\n====================================================\n")

print("\n==================== Full Stats ====================\n")

print("Our get_cpu_stats():")
print(get_cpu_stats())

print("\npsutil reference:")
print({
    "overall": psutil_overall,
    "per_core": psutil_per_core,
    "freq": psutil.cpu_freq(),
    "logical": psutil.cpu_count(logical=True),
    "physical": psutil.cpu_count(logical=False),
})
print("\n====================================================\n")

#-------------------------------------------------------------
#-------------------------------------------------------------

# MEMORY TESTING

#print("---------- Memory Usage ----------")

#print()
#print("Memory: ", get_mem_usage())

#print()

#vm = psutil.virtual_memory()
#print("psutil Total:", vm.total)
#print("psutil Used:", vm.used)
#print("psutil Available:", vm.available)
#print("psutil Percent:", vm.percent, "%")
#print()
