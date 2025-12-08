# ============================================================================
# 1. multithread_test.py - Test multi-threaded process detection (STAT: 'l')
# ============================================================================
"""
multithread_test.py - Create processes with varying thread counts
Tests the 'l' flag in STAT column for multi-threaded processes
"""
import threading
import time
import os

def worker(thread_id, duration):
    """Worker thread that does some light work"""
    print(f"  Thread {thread_id} (TID {threading.get_ident()}) started")
    time.sleep(duration)
    print(f"  Thread {thread_id} done")

def create_multithreaded_process(thread_count=5, duration=60):
    """Create a process with multiple threads"""
    print(f"Creating process with {thread_count} threads")
    print(f"Main PID: {os.getpid()}")
    print(f"Look for STAT='Sl' (sleeping multi-threaded)\n")
    
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=worker, args=(i+1, duration))
        t.start()
        threads.append(t)
    
    print(f"✓ Spawned {thread_count} threads")
    print(f"Check /proc/{os.getpid()}/stat field 19 (num_threads)")
    print(f"Or: ps -o pid,nlwp,stat,command -p {os.getpid()}\n")
    
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n\nInterrupted, waiting for threads to finish...")
        for t in threads:
            t.join(timeout=1)
    
    print("✓ All threads completed")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threads", type=int, default=5)
    parser.add_argument("-d", "--duration", type=int, default=60)
    args = parser.parse_args()
    create_multithreaded_process(args.threads, args.duration)
