#!/bin/bash
# run_all_background.sh - Launch all integration tests simultaneously in background

set -e

SCRIPT_DIR="integration_tests"
DURATION=120  # Default duration

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Launch all integration tests simultaneously in background

OPTIONS:
    -h, --help              Show this help message
    -d, --duration SECONDS  Set duration for tests (default: 120)
    -k, --kill              Kill all running test processes
    -s, --status            Show status of running tests

EXAMPLES:
    $0                      # Run all tests for 120 seconds
    $0 -d 180              # Run all tests for 180 seconds
    $0 --status            # Check running tests
    $0 --kill              # Stop all tests

NOTE: Make sure your monitoring tool is running before launching tests!
EOF
}

kill_tests() {
    print_header "Killing All Test Processes"
    
    pkill -f "create_zombie.py" 2>/dev/null && echo "✓ Killed zombie test" || echo "✗ No zombie test running"
    pkill -f "memory_load.py" 2>/dev/null && echo "✓ Killed memory test" || echo "✗ No memory test running"
    pkill -f "multithread_test.py" 2>/dev/null && echo "✓ Killed multithread test" || echo "✗ No multithread test running"
    pkill -f "priority_test.py" 2>/dev/null && echo "✓ Killed priority test" || echo "✗ No priority test running"
    pkill -f "session_leader_test.py" 2>/dev/null && echo "✓ Killed session test" || echo "✗ No session test running"
    pkill -f "state_transition_test.py" 2>/dev/null && echo "✓ Killed state test" || echo "✗ No state test running"
    pkill -f "rapid_process_test.py" 2>/dev/null && echo "✓ Killed rapid test" || echo "✗ No rapid test running"
    pkill -f "foreground_test.py" 2>/dev/null && echo "✓ Killed foreground test" || echo "✗ No foreground test running"
    
    echo -e "\n${GREEN}All test processes terminated${NC}"
}

show_status() {
    print_header "Running Test Processes"
    
    echo "Zombie Test:"
    pgrep -fa "create_zombie.py" || echo "  Not running"
    
    echo -e "\nMemory Test:"
    pgrep -fa "memory_load.py" || echo "  Not running"
    
    echo -e "\nMultithread Test:"
    pgrep -fa "multithread_test.py" || echo "  Not running"
    
    echo -e "\nPriority Test:"
    pgrep -fa "priority_test.py" || echo "  Not running"
    
    echo -e "\nSession Leader Test:"
    pgrep -fa "session_leader_test.py" || echo "  Not running"
    
    echo -e "\nState Transition Test:"
    pgrep -fa "state_transition_test.py" || echo "  Not running"
    
    echo -e "\nRapid Process Test:"
    pgrep -fa "rapid_process_test.py" || echo "  Not running"
    
    echo -e "\nForeground Test:"
    pgrep -fa "foreground_test.py" || echo "  Not running"
    
    echo -e "\n${BLUE}Total test processes:${NC} $(pgrep -fc "integration_tests" || echo 0)"
}

run_all_background() {
    print_header "Launching All Integration Tests in Background"
    echo -e "${YELLOW}Duration: ${DURATION} seconds${NC}"
    echo -e "${YELLOW}Make sure your monitoring tool is running!${NC}\n"
    
    # Create log directory
    mkdir -p logs
    
    echo "Launching tests..."
    
    # 1. Zombie processes
    python3 "$SCRIPT_DIR/create_zombie.py" -c 3 -d $DURATION > logs/zombie.log 2>&1 &
    PIDS[0]=$!
    echo "  [PID $!] Zombie test"
    
    # 2. Memory load
    python3 "$SCRIPT_DIR/memory_load.py" -d $DURATION > logs/memory.log 2>&1 &
    PIDS[1]=$!
    echo "  [PID $!] Memory load test"
    
    # 3. Multi-threaded
    python3 "$SCRIPT_DIR/multithread_test.py" -t 10 -d $DURATION > logs/multithread.log 2>&1 &
    PIDS[2]=$!
    echo "  [PID $!] Multithread test"
    
    # 4. Priority
    python3 "$SCRIPT_DIR/priority_test.py" -d $DURATION > logs/priority.log 2>&1 &
    PIDS[3]=$!
    echo "  [PID $!] Priority test"
    
    # 5. Session leader
    python3 "$SCRIPT_DIR/session_leader_test.py" -d $DURATION > logs/session.log 2>&1 &
    PIDS[4]=$!
    echo "  [PID $!] Session leader test"
    
    # 6. State transitions (more cycles for longer duration)
    CYCLES=$((DURATION / 5))
    python3 "$SCRIPT_DIR/state_transition_test.py" -c $CYCLES > logs/state.log 2>&1 &
    PIDS[5]=$!
    echo "  [PID $!] State transition test"
    
    # 7. Rapid process spawn
    python3 "$SCRIPT_DIR/rapid_process_test.py" -r 5 -d $DURATION > logs/rapid.log 2>&1 &
    PIDS[6]=$!
    echo "  [PID $!] Rapid process test"
    
    # 8. Foreground test (note: will be in background, so no + flag)
    python3 "$SCRIPT_DIR/foreground_test.py" > logs/foreground.log 2>&1 &
    PIDS[7]=$!
    echo "  [PID $!] Foreground test"
    
    echo -e "\n${GREEN}✓ All tests launched!${NC}"
    echo -e "\nTest PIDs: ${PIDS[@]}"
    echo -e "\nLogs available in: logs/"
    echo -e "  - logs/zombie.log"
    echo -e "  - logs/memory.log"
    echo -e "  - logs/multithread.log"
    echo -e "  - logs/priority.log"
    echo -e "  - logs/session.log"
    echo -e "  - logs/state.log"
    echo -e "  - logs/rapid.log"
    echo -e "  - logs/foreground.log"
    
    echo -e "\n${YELLOW}Commands:${NC}"
    echo "  Check status:  $0 --status"
    echo "  Kill all:      $0 --kill"
    echo "  View logs:     tail -f logs/*.log"
    echo "  Job control:   jobs, fg, bg"
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_usage
        exit 0
        ;;
    -k|--kill)
        kill_tests
        exit 0
        ;;
    -s|--status)
        show_status
        exit 0
        ;;
    -d|--duration)
        DURATION=$2
        run_all_background
        exit 0
        ;;
    "")
        run_all_background
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
