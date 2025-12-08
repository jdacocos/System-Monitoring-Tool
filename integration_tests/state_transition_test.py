# ============================================================================
# 7. state_transition_test.py - Test process state changes
# ============================================================================
"""
state_transition_test.py - Process that cycles through different states
Tests monitoring of R (running) and S (sleeping) states
"""
import time
import os

def cpu_burst(duration):
    """Generate CPU load (R state)"""
    print(f"  → Running (R state) for {duration}s")
    end = time.time() + duration
    count = 0
    while time.time() < end:
        count += 1  # Busy loop
    return count

def sleep_period(duration):
    """Sleep (S state)"""
    print(f"  → Sleeping (S state) for {duration}s")
    time.sleep(duration)

def cycle_states(cycles=10):
    """Alternate between running and sleeping"""
    print(f"PID {os.getpid()} cycling through states")
    print("Watch STAT column change between 'R' and 'S'\n")
    
    for i in range(cycles):
        print(f"Cycle {i+1}/{cycles}")
        cpu_burst(2)
        sleep_period(3)
    
    print("\n✓ Completed all state transitions")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cycles", type=int, default=10)
    args = parser.parse_args()
    cycle_states(args.cycles)
