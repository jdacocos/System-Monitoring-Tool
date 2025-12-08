#!/usr/bin/env python3
import time
big_list = []

MAX_CHUNKS = 500  # total ~5 GB if each chunk is 10 MB
chunk_size = 10_000_000

try:
    for _ in range(MAX_CHUNKS):
        big_list.append("A" * chunk_size)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

# Keep process alive without adding more memory
while True:
    time.sleep(1)
