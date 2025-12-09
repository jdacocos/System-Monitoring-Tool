#!/bin/bash
# run_integration_test.sh - Launch all integration tests in background

set -e

# Test directory
TEST_DIR="./integration_tests"

# Create logs directory
mkdir -p logs

echo "=========================================="
echo "Starting Integration Tests"
echo "=========================================="
echo ""

# 1. Zombie test
python3 "$TEST_DIR/create_zombie.py" > logs/zombie.log 2>&1 &
echo "[PID $!] Zombie test started"

# 2. Memory load test
python3 "$TEST_DIR/memory_load.py" > logs/memory.log 2>&1 &
echo "[PID $!] Memory load test started"

# 3. Multi-thread test
python3 "$TEST_DIR/multithread_test.py" > logs/multithread.log 2>&1 &
echo "[PID $!] Multi-thread test started"

# 4. Parent-child hierarchy test
python3 "$TEST_DIR/parent_child_test.py" > logs/parent_child.log 2>&1 &
echo "[PID $!] Parent-child test started"

# 5. Stress test
python3 "$TEST_DIR/stress_test.py" > logs/stress.log 2>&1 &
echo "[PID $!] Stress test started"

echo ""
echo "=========================================="
echo "All tests launched!"
echo "=========================================="
echo ""
echo "Logs available in: logs/"
echo "  - logs/zombie.log"
echo "  - logs/memory.log"
echo "  - logs/multithread.log"
echo "  - logs/parent_child.log"
echo "  - logs/stress.log"
echo ""
echo "To stop all tests:"
echo "  pkill -f 'create_zombie.py|memory_load.py|multithread_test.py|parent_child_test.py|stress_test.py'"
echo ""
echo "To view logs:"
echo "  tail -f logs/*.log"
