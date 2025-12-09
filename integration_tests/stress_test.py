#!/usr/bin/env python3
"""
stress_test.py - Combined CPU and memory stress test
Creates high CPU usage and memory consumption to test monitoring tool
"""
import time

# Allocate memory in chunks
memory_chunks = []
chunk_size = 10_000_000  # 10 MB per chunk
max_chunks = 100  # ~1 GB total

# Phase 1: Allocate memory
try:
    for i in range(max_chunks):
        memory_chunks.append("X" * chunk_size)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

# Phase 2: CPU stress while holding memory
try:
    counter = 0
    while True:
        # Heavy CPU work
        for i in range(1000000):
            counter += i * i
            counter = counter % 1000000  # Prevent overflow
        
        time.sleep(0.01)  # Tiny sleep to prevent complete lockup
        
except KeyboardInterrupt:
    pass
