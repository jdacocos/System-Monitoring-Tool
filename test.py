# File to test modules independently

from cpu import get_cpu_usage
from memory import get_mem_usage

print("CPU: ", get_cpu_usage(), "%")
print("Memory: ", get_mem_usage())

# Testing
import psutil

print("psutil CPU: ", psutil.cpu_percent(interval=0.1), "%")
print("psutil Memory: ", psutil.virtual_memory().percent, "% used00")
