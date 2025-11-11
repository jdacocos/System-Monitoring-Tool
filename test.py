# File to test modules independently

import os
from cpu import get_cpu_usage

print("PID: ", os.getpid())
print("CPU: ", get_cpu_usage(), "%")


# Testing
import psutil
print("psutil CPU: ", psutil.cpu_percent(interval=0.1), "%")
