# File to test modules independently

import psutil

from cpu import get_cpu_usage
from memory import get_mem_usage

#-------------------------------------------------------------
#-------------------------------------------------------------

# CPU TESTING

print("---------- CPU Total Usage ----------")

print()
print("CPU: ", get_cpu_usage(), "%")

print()

print("psutil CPU:", psutil.cpu_percent(interval=0.1), "%")
print()

#-------------------------------------------------------------

print("---------- CPU Per Core Usage ----------")

per_core = psutil.cpu_percent(interval=0.1, percpu=True)

print()
for i, percent in enumerate(per_core):
    print("psutil Core", i, ":", percent, "%")
print()

#-------------------------------------------------------------

print("---------- CPU Frequency ----------")

freq = psutil.cpu_freq()

print()
print("psutil Current:", freq.current, "MHz")
print("psutil Min:", freq.min, "MHz")
print("psutil Max:", freq.max, "MHz")
print()

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
