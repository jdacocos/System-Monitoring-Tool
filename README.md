# System Monitoring Tool
A lightweight system monitoring application designed to retrieve, process, and display real-time system information with smooth UI integration and responsive process control.

---

## Installation

### **Prerequisites**
- Python 3.10 or later
- pip package manager
- A Unix-based operating system (Linux recommended)

### **Setup**
1. **Clone the repository**
```bash
git clone https://github.com/your-username/system-monitoring-tool.git
cd system-monitoring-tool
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python3 main.py
```

Some features (e.g., lowering nice values) may require elevated privileges:
```bash
sudo python3 main.py
```

---

## Features
- **Real-time process retrieval** - Efficiently gathers live process information directly from the operating system.
- **Structured data pipeline** - Normalizes and formats raw system data for consistent UI consumption.
- **CPU monitoring** - Displays live CPU usage across all available cores.
- **Memory monitoring** - Tracks system memory usage, swap activity, and overall resource consumption.
- **Process page** - Provides detailed per-process information such as PID, CPU usage, memory usage, state, and TTY.
- **Signal-based process control** - Supports responsive and safe signalling mechanisms such as `SIGTERM` and `SIGKILL`.
- **Process termination (kill)** - Users can terminate running processes directly from the UI.
- **Adjust process priority (nice value)**  
  - Users can increase a process's nice value (lower priority) without elevated privileges.  
  - Lowering the nice value (raising priority) requires elevated permissions (`sudo`).  
  - Linux restricts non-root users to raising the nice value only, and typically only once.
- **Backend–Frontend integration layer** - Bridges system-level data with the application interface for seamless interaction.

---

## Working Features
The following sections of the tool are fully implemented and functional:
- **CPU Page** - Real-time CPU load visualization.  
- **Memory Page** - Accurate system memory and swap tracking.  
- **Process Page** - Full process listing, live updates, process control, and priority adjustment.

These components form the current stable core of the system.

---

## Testing

### **Code Quality and Formatting**

#### Frontend Code Cleanup
Run automated code formatting and linting for frontend modules:
```bash
./clean_frontend.sh
```
This script runs:
- `autoflake` - Removes unused imports and variables
- `pylint` - Lints code to PEP 8 standards
- `black` - Formats code consistently

#### Backend Code Cleanup and Testing
Run automated code formatting, linting, and tests for backend modules:
```bash
./run_test.sh
```
This script runs:
- `autoflake` - Removes unused imports and variables
- `pylint` - Lints code to PEP 8 standards (target: 10/10 rating)
- `black` - Formats code consistently
- `pytest` - Runs all backend unit tests

### **Integration Testing**

Integration tests validate specific system behaviors and edge cases. These tests create real processes to verify the monitoring tool's accuracy.

#### Available Integration Tests
- **`create_zombie.py`** - Creates zombie processes (STATE: Z)
- **`multithread_test.py`** - Spawns multi-threaded processes (STATE: Sl, Rl)
- **`memory_load.py`** - Allocates ~5GB memory to test memory tracking
- **`parent_child_test.py`** - Creates 3-level process hierarchy (parent → children → grandchildren)
- **`stress_test.py`** - High CPU + high memory load test

#### Running Integration Tests

**Run all tests simultaneously:**
```bash
./run_integration_test.sh
```
This launches all tests in the background with output redirected to `logs/` directory.

**Run individual tests:**
```bash
# Zombie process test
python3 ./integration_tests/create_zombie.py &

# Memory load test
python3 ./integration_tests/memory_load.py &

# Multi-threaded process test
python3 ./integration_tests/multithread_test.py &

# Parent-child hierarchy test
python3 ./integration_tests/parent_child_test.py &

# Stress test (high CPU + memory)
python3 ./integration_tests/stress_test.py &
```

**Stop all running tests:**
```bash
pkill -f 'create_zombie.py|memory_load.py|multithread_test.py|parent_child_test.py|stress_test.py'
```

**View test logs:**
```bash
tail -f logs/*.log
```

#### Important Notes
- All integration tests run in the background to avoid interfering with the monitoring tool's UI
- Running all tests simultaneously creates significant CPU load (10+ processes) - expect slower refresh rates
- For optimal performance, run tests individually or in small groups (2-3 at a time)
- Tests continue running until manually terminated with `pkill` or Ctrl+C

---

## Stretch Goals
Future enhancements planned for full-feature completion include:

- **Dashboard (Full Low-Level Reimplementation)**  
  Rebuild the dashboard using direct system calls and the Python `os` module for maximum accuracy and minimal overhead.

- **Disk Monitoring**  
  Track disk I/O usage, device throughput, read/write statistics, and filesystem usage.

- **Network Monitoring**  
  Monitor network interfaces, bandwidth, packet statistics, and connection states.

- **PPID Implementation**  
  Add Parent Process ID (PPID) column to better visualize process hierarchies and relationships.

These goals will be integrated once the core functionality has matured.

---

## Purpose
The System Monitoring Tool's backend establishes a reliable foundation for:
- Accurate and immediate system insight.
- Efficient process management operations.
- Interactive and responsive user experiences.
- Future expansion of functionality across the entire application.

---

## Project Structure
```
system-monitoring-tool/
├── main.py                          # Application entry point
├── README.md                        # Project documentation
├── requirements.txt                 # Python dependencies
├── structure.txt                    # Project structure tree
│
├── clean_frontend.sh                # Frontend code quality (autoflake, pylint, black)
├── run_test.sh                      # Backend testing and quality (autoflake, pylint, black, pytest)
├── run_integration_test.sh          # Integration test launcher
│
├── backend/                         # Backend data processing modules
│   ├── __init__.py
│   ├── cpu_info.py                  # CPU statistics from /proc/stat, /proc/cpuinfo
│   ├── memory_info.py               # Memory statistics from /proc/meminfo, /proc/vmstat
│   ├── process.py                   # Main process data aggregation
│   ├── process_struct.py            # ProcessInfo data structure
│   ├── process_constants.py         # Process-related constants
│   ├── file_helpers.py              # File I/O utilities
│   └── process_util/                # Process attribute parsers
│       ├── __init__.py
│       ├── pids.py                  # PID enumeration from /proc
│       ├── command.py               # Command name from /proc/[pid]/cmdline
│       ├── cpu_percent.py           # CPU percentage calculation
│       ├── mem_percent.py           # Memory percentage calculation
│       ├── vsz.py                   # Virtual memory size
│       ├── rss.py                   # Resident memory size
│       ├── stat.py                  # Process state flags
│       ├── nice.py                  # Nice value (priority)
│       ├── tty.py                   # Controlling terminal
│       ├── user.py                  # Process owner from /etc/passwd
│       ├── start.py                 # Process start time
│       └── time.py                  # CPU time consumed
│
├── frontend/                        # Terminal UI using curses
│   ├── __init__.py
│   ├── interface.py                 # Main UI controller
│   ├── pages/                       # Page-specific renderers
│   │   ├── __init__.py
│   │   ├── cpu_page.py              # CPU monitoring page
│   │   ├── memory_page.py           # Memory monitoring page
│   │   ├── dashboard_page.py        # System overview dashboard
│   │   ├── disk_page.py             # Disk I/O monitoring
│   │   ├── network_page.py          # Network monitoring
│   │   └── process_page/            # Process management interface
│   │       ├── process_page.py      # Main process page controller
│   │       ├── process_display.py   # Process table rendering
│   │       ├── process_input.py     # User input handling
│   │       ├── process_operations.py # Kill, renice operations
│   │       ├── process_state.py     # Process page state management
│   │       └── process_page_constants.py # Constants and configurations
│   └── utils/                       # UI utility functions
│       ├── input_helpers.py         # Input processing utilities
│       ├── page_helpers.py          # Page rendering utilities
│       └── ui_helpers.py            # General UI helpers
│
├── integration_tests/               # Integration test suite
│   ├── create_zombie.py             # Zombie process test (STATE: Z)
│   ├── multithread_test.py          # Multi-threaded process test (STATE: Sl, Rl)
│   ├── memory_load.py               # Memory allocation test (~5GB)
│   ├── parent_child_test.py         # Process hierarchy test (3 levels)
│   └── stress_test.py               # CPU + memory stress test
│
├── test_modules/                    # Backend unit tests (pytest)
│   ├── __init__.py
│   ├── test_cpu_info.py             # CPU data parsing tests
│   ├── test_memory_info.py          # Memory data parsing tests
│   ├── test_process.py              # Process aggregation tests
│   ├── test_process_struct.py       # ProcessInfo structure tests
│   ├── test_command.py              # Command parsing tests
│   ├── test_cpu_percent.py          # CPU percentage calculation tests
│   ├── test_mem_percent.py          # Memory percentage calculation tests
│   ├── test_vsz.py                  # Virtual memory tests
│   ├── test_rss.py                  # Resident memory tests
│   ├── test_stat.py                 # Process state tests
│   ├── test_nice.py                 # Nice value tests
│   ├── test_tty.py                  # TTY parsing tests
│   ├── test_user.py                 # User lookup tests
│   ├── test_start.py                # Start time tests
│   ├── test_time.py                 # CPU time tests
│   └── test_pids.py                 # PID enumeration tests
│
└── logs/                            # Integration test output (created at runtime)
    ├── zombie.log
    ├── memory.log
    ├── multithread.log
    ├── parent_child.log
    └── stress.log
```