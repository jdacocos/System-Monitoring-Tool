#!/usr/bin/env python3
"""
create_zombie.py - Generate zombie processes for testing

A zombie process is created when:
1. A child process exits
2. The parent doesn't call wait() to collect the exit status
3. The child becomes a zombie (Z state) until parent collects it
"""

import os
import sys
import time

def create_zombie(count=1, duration=60):
    """
    Create zombie processes that last for a specified duration.
    
    Parameters:
        count: Number of zombie processes to create
        duration: How long to keep zombies alive (seconds)
    """
    print(f"Creating {count} zombie process(es) for {duration} seconds...")
    print(f"Parent PID: {os.getpid()}")
    
    zombies = []
    
    for i in range(count):
        pid = os.fork()
        
        if pid == 0:  # Child process
            # Child exits immediately, becoming a zombie
            print(f"Child {i+1} (PID {os.getpid()}) exiting...")
            sys.exit(0)
        else:  # Parent process
            zombies.append(pid)
            print(f"Created zombie {i+1}: PID {pid}")
    
    print(f"\n✓ Created {count} zombie(s)")
    print(f"Parent PID: {os.getpid()}")
    print(f"Zombie PIDs: {zombies}")
    print(f"\nCheck with: ps -o pid,stat,command -p {','.join(map(str, zombies))}")
    print(f"Or in your monitor: Look for STAT='Z'\n")
    
    # Keep parent alive (not calling wait() so children remain zombies)
    print(f"Keeping zombies alive for {duration} seconds...")
    print("Press Ctrl+C to reap zombies and exit early\n")
    
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\n\nCtrl+C detected. Reaping zombies...")
    
    # Reap all zombies
    for pid in zombies:
        try:
            os.waitpid(pid, 0)
            print(f"Reaped zombie PID {pid}")
        except ChildProcessError:
            print(f"Zombie PID {pid} already reaped")
    
    print("\n✓ All zombies cleaned up")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create zombie processes for testing")
    parser.add_argument("-c", "--count", type=int, default=1, 
                        help="Number of zombies to create (default: 1)")
    parser.add_argument("-d", "--duration", type=int, default=60,
                        help="Duration in seconds (default: 60)")
    
    args = parser.parse_args()
    
    create_zombie(args.count, args.duration)
