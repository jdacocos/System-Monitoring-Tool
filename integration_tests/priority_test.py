# ============================================================================
# 2. priority_test.py - Test high/low priority processes (STAT: '<', 'N')
# ============================================================================
"""
priority_test.py - Create processes with different nice values
Tests the '<' (high priority) and 'N' (low priority) flags
"""
import os
import time
import subprocess

def test_priority_processes(duration=60):
    """Create processes with different priorities"""
    print("Testing process priorities...")
    print(f"Parent PID: {os.getpid()}\n")
    
    # High priority process (nice < 0, requires root)
    print("1. High priority process (nice = -10)")
    print("   Expected STAT flag: '<' (high priority)")
    try:
        subprocess.Popen(["nice", "-n", "-10", "sleep", str(duration)])
        print("   ✓ Started (requires sudo/root)\n")
    except PermissionError:
        print("   ✗ Permission denied (needs root). Skipping.\n")
    
    # Normal priority process (nice = 0)
    print("2. Normal priority process (nice = 0)")
    print("   Expected STAT flag: none")
    subprocess.Popen(["sleep", str(duration)])
    print("   ✓ Started\n")
    
    # Low priority process (nice > 0)
    print("3. Low priority process (nice = 10)")
    print("   Expected STAT flag: 'N' (low priority)")
    subprocess.Popen(["nice", "-n", "10", "sleep", str(duration)])
    print("   ✓ Started\n")
    
    # Very low priority process (nice = 19)
    print("4. Very low priority process (nice = 19)")
    print("   Expected STAT flag: 'N' (low priority)")
    subprocess.Popen(["nice", "-n", "19", "sleep", str(duration)])
    print("   ✓ Started\n")
    
    print(f"All test processes running for {duration} seconds")
    print("Check with: ps -o pid,ni,stat,command | grep sleep")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--duration", type=int, default=60)
    args = parser.parse_args()
    test_priority_processes(args.duration)
