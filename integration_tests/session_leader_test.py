# ============================================================================
# 4. session_leader_test.py - Test session leader detection (STAT: 's')
# ============================================================================
"""
session_leader_test.py - Create session leader processes
Tests the 's' flag in STAT column
"""
import os
import time
import subprocess

def create_session_leader(duration=60):
    """Create a session leader process"""
    print("Creating session leader process...")
    print(f"Current PID: {os.getpid()}")
    print(f"Current SID: {os.getsid(0)}\n")
    
    # Create new session using setsid
    cmd = f"setsid sleep {duration}"
    proc = subprocess.Popen(cmd, shell=True)
    
    print(f"✓ Created session leader")
    print(f"Process PID: {proc.pid}")
    print(f"Expected STAT flag: 's' (session leader)")
    print(f"\nCheck with: ps -o pid,sid,stat,command -p {proc.pid}")
    print("In session leaders, PID == SID")
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n\nCleaning up...")
        proc.terminate()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--duration", type=int, default=60)
    args = parser.parse_args()
    create_session_leader(args.duration)
