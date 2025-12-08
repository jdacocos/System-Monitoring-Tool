# ============================================================================
# 6. rapid_process_test.py - Test rapid process creation/termination
# ============================================================================
"""
rapid_process_test.py - Stress test with rapid process creation
Tests monitor's ability to handle quickly changing process list
"""
import subprocess
import time
import os

def rapid_process_spawn(rate=10, duration=60):
    """Spawn processes rapidly to test monitor stability"""
    print(f"Spawning {rate} processes per second for {duration} seconds")
    print(f"Total processes: ~{rate * duration}")
    print("This tests:")
    print("  - Cache invalidation")
    print("  - Error handling for disappeared processes")
    print("  - UI update performance\n")
    
    start = time.time()
    count = 0
    
    try:
        while time.time() - start < duration:
            # Spawn short-lived processes
            subprocess.Popen(["sleep", "0.1"])
            count += 1
            time.sleep(1.0 / rate)
            
            if count % 50 == 0:
                print(f"Spawned {count} processes...")
    
    except KeyboardInterrupt:
        print("\n\nStopped early")
    
    print(f"\n✓ Spawned {count} total processes")
    print("Your monitor should have handled many /proc read errors gracefully")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rate", type=int, default=10)
    parser.add_argument("-d", "--duration", type=int, default=60)
    args = parser.parse_args()
    rapid_process_spawn(args.rate, args.duration)
