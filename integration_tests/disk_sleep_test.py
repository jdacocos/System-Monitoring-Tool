# ============================================================================
# 3. disk_sleep_test.py - Test uninterruptible sleep (STAT: 'D')
# ============================================================================
"""
disk_sleep_test.py - Create process in uninterruptible sleep
Tests the 'D' state (disk sleep / uninterruptible sleep)
Note: 'D' state is hard to create artificially and usually brief
"""
import subprocess
import os

def create_disk_sleep():
    """
    Attempt to create a process in 'D' state.
    This is difficult to do reliably, but we can try with sync operations.
    """
    print("Attempting to create uninterruptible sleep (D state)...")
    print("Note: 'D' state is typically very brief and hard to catch\n")
    
    print("Method 1: Continuous sync operations")
    print(f"PID: {os.getpid()}")
    print("Run this and quickly check your monitor:")
    print("  while true; do sync; done")
    print("\nMethod 2: Large file I/O")
    print("  dd if=/dev/zero of=/tmp/testfile bs=1M count=1000 oflag=sync")
    
    print("\n'D' state processes are usually:")
    print("  - Waiting for disk I/O")
    print("  - In kernel system calls")
    print("  - Cannot be interrupted by signals")
    print("\nTo observe, run your monitor and simultaneously run:")
    print("  dd if=/dev/urandom of=/tmp/test bs=1G count=1 conv=fsync")

if __name__ == "__main__":
    create_disk_sleep()
