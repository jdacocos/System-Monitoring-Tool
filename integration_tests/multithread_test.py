#!/usr/bin/env python3
"""
multithread_test.py - Create processes with varying thread counts and behaviors
Tests the 'l' flag in STAT column for multi-threaded processes

The 'l' flag indicates: is multi-threaded (using CLONE_THREAD)
Common STAT values:
  - Sl  : Sleeping multi-threaded
  - Rl  : Running multi-threaded
  - Dl  : Disk sleep multi-threaded
"""
import threading
import time
import os
import sys
import argparse
from datetime import datetime

# Global flag for graceful shutdown
shutdown_flag = threading.Event()

def cpu_intensive_worker(thread_id, duration):
    """
    Worker that does CPU-intensive work (STAT: Rl)
    Performs calculations to show running state
    """
    print(f"  [CPU] Thread {thread_id} (TID {threading.get_ident()}) started")
    start = time.time()
    counter = 0
    
    while not shutdown_flag.is_set() and (time.time() - start < duration):
        # CPU work: calculate prime numbers
        for num in range(2, 1000):
            if all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
                counter += 1
        # Brief yield to allow other threads
        time.sleep(0.01)
    
    print(f"  [CPU] Thread {thread_id} done (computed {counter} iterations)")

def sleeping_worker(thread_id, duration):
    """
    Worker that mostly sleeps (STAT: Sl)
    This is the most common state for idle threads
    """
    print(f"  [SLEEP] Thread {thread_id} (TID {threading.get_ident()}) started")
    start = time.time()
    
    while not shutdown_flag.is_set() and (time.time() - start < duration):
        time.sleep(1)
    
    print(f"  [SLEEP] Thread {thread_id} done")

def io_worker(thread_id, duration):
    """
    Worker that does I/O operations (STAT: Dl occasionally)
    Writes to disk to potentially trigger disk sleep state
    """
    print(f"  [I/O] Thread {thread_id} (TID {threading.get_ident()}) started")
    start = time.time()
    filename = f"/tmp/thread_io_{os.getpid()}_{thread_id}.tmp"
    
    try:
        while not shutdown_flag.is_set() and (time.time() - start < duration):
            # Write data
            with open(filename, "wb") as f:
                data = b"x" * (1024 * 1024)  # 1MB
                f.write(data)
                f.flush()
                os.fsync(f.fileno())  # Force sync to disk
            
            # Read it back
            with open(filename, "rb") as f:
                _ = f.read()
            
            time.sleep(0.5)
    finally:
        try:
            os.remove(filename)
        except:
            pass
    
    print(f"  [I/O] Thread {thread_id} done")

def periodic_worker(thread_id, duration, interval=2):
    """
    Worker that alternates between working and sleeping
    Shows state transitions: Sl -> Rl -> Sl
    """
    print(f"  [PERIODIC] Thread {thread_id} (TID {threading.get_ident()}) started")
    start = time.time()
    
    while not shutdown_flag.is_set() and (time.time() - start < duration):
        # Work phase (running)
        for _ in range(1000000):
            _ = _ + 1
        
        # Sleep phase
        time.sleep(interval)
    
    print(f"  [PERIODIC] Thread {thread_id} done")

def lock_contention_worker(thread_id, duration, shared_lock):
    """
    Worker that competes for a lock
    May show different states depending on lock availability
    """
    print(f"  [LOCK] Thread {thread_id} (TID {threading.get_ident()}) started")
    start = time.time()
    acquisitions = 0
    
    while not shutdown_flag.is_set() and (time.time() - start < duration):
        with shared_lock:
            # Critical section - do some work
            time.sleep(0.1)
            acquisitions += 1
        
        # Non-critical section
        time.sleep(0.05)
    
    print(f"  [LOCK] Thread {thread_id} done (acquired lock {acquisitions} times)")

def create_multithreaded_process(config):
    """Create a process with multiple threads of different types"""
    print("=" * 70)
    print("MULTI-THREADED PROCESS TEST")
    print("=" * 70)
    print(f"\nMain PID: {os.getpid()}")
    print(f"Duration: {config['duration']} seconds")
    print(f"Total threads: {config['total_threads']}")
    print(f"\nExpected STAT flags:")
    print("  - 'l' = multi-threaded (CLONE_THREAD)")
    print("  - Sl  = Sleeping multi-threaded")
    print("  - Rl  = Running multi-threaded")
    print("  - Dl  = Disk sleep multi-threaded")
    print("\n" + "=" * 70)
    print("THREAD BREAKDOWN")
    print("=" * 70)
    
    threads = []
    shared_lock = threading.Lock()
    
    # CPU-intensive threads (will show Rl)
    if config['cpu_threads'] > 0:
        print(f"\nCPU-intensive threads: {config['cpu_threads']}")
        for i in range(config['cpu_threads']):
            t = threading.Thread(
                target=cpu_intensive_worker,
                args=(f"CPU-{i+1}", config['duration']),
                name=f"CPUWorker-{i+1}"
            )
            t.start()
            threads.append(t)
    
    # Sleeping threads (will show Sl)
    if config['sleep_threads'] > 0:
        print(f"Sleeping threads: {config['sleep_threads']}")
        for i in range(config['sleep_threads']):
            t = threading.Thread(
                target=sleeping_worker,
                args=(f"SLEEP-{i+1}", config['duration']),
                name=f"SleepWorker-{i+1}"
            )
            t.start()
            threads.append(t)
    
    # I/O threads (may show Dl briefly)
    if config['io_threads'] > 0:
        print(f"I/O threads: {config['io_threads']}")
        for i in range(config['io_threads']):
            t = threading.Thread(
                target=io_worker,
                args=(f"IO-{i+1}", config['duration']),
                name=f"IOWorker-{i+1}"
            )
            t.start()
            threads.append(t)
    
    # Periodic threads (alternate Sl/Rl)
    if config['periodic_threads'] > 0:
        print(f"Periodic threads: {config['periodic_threads']}")
        for i in range(config['periodic_threads']):
            t = threading.Thread(
                target=periodic_worker,
                args=(f"PERIODIC-{i+1}", config['duration']),
                name=f"PeriodicWorker-{i+1}"
            )
            t.start()
            threads.append(t)
    
    # Lock contention threads
    if config['lock_threads'] > 0:
        print(f"Lock contention threads: {config['lock_threads']}")
        for i in range(config['lock_threads']):
            t = threading.Thread(
                target=lock_contention_worker,
                args=(f"LOCK-{i+1}", config['duration'], shared_lock),
                name=f"LockWorker-{i+1}"
            )
            t.start()
            threads.append(t)
    
    print(f"\n✓ Spawned {len(threads)} threads total")
    print("\n" + "=" * 70)
    print("VERIFICATION COMMANDS")
    print("=" * 70)
    print(f"\n1. Check thread count:")
    print(f"   ps -o pid,nlwp,stat,command -p {os.getpid()}")
    print(f"\n2. Check /proc filesystem:")
    print(f"   cat /proc/{os.getpid()}/status | grep Threads")
    print(f"\n3. List all threads:")
    print(f"   ps -T -p {os.getpid()}")
    print(f"\n4. Watch in real-time:")
    print(f"   watch -n 0.5 'ps -T -o pid,tid,stat,pcpu,comm -p {os.getpid()}'")
    print("\n" + "=" * 70)
    print("RUNNING - Monitor your process viewer")
    print("=" * 70)
    print("\nPress Ctrl+C to stop\n")
    
    start_time = time.time()
    
    try:
        # Progress updates
        while any(t.is_alive() for t in threads):
            elapsed = int(time.time() - start_time)
            alive_count = sum(1 for t in threads if t.is_alive())
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Elapsed: {elapsed}s / {config['duration']}s | "
                  f"Active threads: {alive_count}/{len(threads)}", end="", flush=True)
            time.sleep(1)
            
            if elapsed >= config['duration']:
                shutdown_flag.set()
                break
    
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted! Shutting down gracefully...")
        shutdown_flag.set()
    
    # Wait for all threads
    print("\nWaiting for threads to finish...")
    for t in threads:
        t.join(timeout=5)
    
    print("\n\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)
    print(f"Total runtime: {int(time.time() - start_time)} seconds")
    print(f"Threads completed: {sum(1 for t in threads if not t.is_alive())}/{len(threads)}")

def main():
    parser = argparse.ArgumentParser(
        description="Create multi-threaded processes with various behaviors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Thread Types:
  CPU      - CPU-intensive workers (state: Rl)
  SLEEP    - Mostly sleeping workers (state: Sl)
  I/O      - Disk I/O workers (may show Dl)
  PERIODIC - Alternating work/sleep (transitions)
  LOCK     - Lock contention workers

Examples:
  %(prog)s                           # Default: 10 threads mixed
  %(prog)s -t 20 -d 120             # 20 threads for 2 minutes
  %(prog)s --cpu 5 --sleep 10       # 5 CPU + 10 sleep threads
  %(prog)s --io 3 --periodic 3      # 3 I/O + 3 periodic threads
  %(prog)s --preset heavy           # CPU-heavy workload
        """
    )
    
    parser.add_argument("-t", "--threads", type=int,
                       help="Total threads (distributed across types)")
    parser.add_argument("-d", "--duration", type=int, default=60,
                       help="Duration in seconds (default: 60)")
    
    # Individual thread type counts
    parser.add_argument("--cpu", type=int,
                       help="Number of CPU-intensive threads")
    parser.add_argument("--sleep", type=int,
                       help="Number of sleeping threads")
    parser.add_argument("--io", type=int,
                       help="Number of I/O threads")
    parser.add_argument("--periodic", type=int,
                       help="Number of periodic threads")
    parser.add_argument("--lock", type=int,
                       help="Number of lock contention threads")
    
    # Presets
    parser.add_argument("--preset", choices=["balanced", "heavy", "io", "mixed"],
                       help="Use predefined thread configuration")
    
    parser.add_argument("-q", "--quiet", action="store_true",
                       help="Quiet mode - minimal output (better for background)")
    
    args = parser.parse_args()
    
    # Set quiet mode globally
    if args.quiet:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    
    # Configuration
    config = {
        'duration': args.duration,
        'cpu_threads': 0,
        'sleep_threads': 0,
        'io_threads': 0,
        'periodic_threads': 0,
        'lock_threads': 0,
    }
    
    # Handle presets
    if args.preset:
        presets = {
            'balanced': {'cpu_threads': 2, 'sleep_threads': 4, 'io_threads': 2, 'periodic_threads': 2},
            'heavy': {'cpu_threads': 8, 'io_threads': 2},
            'io': {'io_threads': 5, 'sleep_threads': 5},
            'mixed': {'cpu_threads': 2, 'sleep_threads': 2, 'io_threads': 2, 'periodic_threads': 2, 'lock_threads': 2},
        }
        config.update(presets[args.preset])
    
    # Handle individual arguments
    if args.cpu is not None:
        config['cpu_threads'] = args.cpu
    if args.sleep is not None:
        config['sleep_threads'] = args.sleep
    if args.io is not None:
        config['io_threads'] = args.io
    if args.periodic is not None:
        config['periodic_threads'] = args.periodic
    if args.lock is not None:
        config['lock_threads'] = args.lock
    
    # Handle total threads argument
    if args.threads:
        total_specified = sum([
            config['cpu_threads'],
            config['sleep_threads'],
            config['io_threads'],
            config['periodic_threads'],
            config['lock_threads']
        ])
        
        if total_specified == 0:
            # Distribute evenly
            per_type = args.threads // 5
            remainder = args.threads % 5
            config['cpu_threads'] = per_type + (1 if remainder > 0 else 0)
            config['sleep_threads'] = per_type + (1 if remainder > 1 else 0)
            config['io_threads'] = per_type + (1 if remainder > 2 else 0)
            config['periodic_threads'] = per_type + (1 if remainder > 3 else 0)
            config['lock_threads'] = per_type + (1 if remainder > 4 else 0)
    
    # Default if nothing specified
    total = sum([
        config['cpu_threads'],
        config['sleep_threads'],
        config['io_threads'],
        config['periodic_threads'],
        config['lock_threads']
    ])
    
    if total == 0:
        # Default balanced configuration
        config['cpu_threads'] = 2
        config['sleep_threads'] = 4
        config['io_threads'] = 2
        config['periodic_threads'] = 2
    
    config['total_threads'] = sum([
        config['cpu_threads'],
        config['sleep_threads'],
        config['io_threads'],
        config['periodic_threads'],
        config['lock_threads']
    ])
    
    create_multithreaded_process(config)

if __name__ == "__main__":
    main()
