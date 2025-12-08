# ============================================================================
# 5. foreground_test.py - Test foreground process detection (STAT: '+')
# ============================================================================
"""
foreground_test.py - Test foreground process detection
Tests the '+' flag (process in foreground process group)
"""
import os
import time

def test_foreground():
    """Demonstrate foreground process"""
    print("Testing foreground process detection...")
    print(f"PID: {os.getpid()}")
    print(f"PGRP: {os.getpgrp()}")
    
    if os.isatty(0):  # Check if stdin is a terminal
        print(f"Foreground PGRP: {os.tcgetpgrp(0)}")
        print("\nThis process should show '+' flag if running in foreground")
        print("Compare with background: ./foreground_test.py &")
    else:
        print("Not running in a terminal")
    
    print("\nSleeping for 30 seconds...")
    print("Check your monitor for STAT flag")
    time.sleep(30)

if __name__ == "__main__":
    test_foreground()
