# System Monitoring Tool

A lightweight, multithreaded system monitoring application designed to retrieve, process, and display real-time system information with smooth UI integration and responsive process control.

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
2. **Install dependencies**
Make sure you have requirements.txt in the project root, then run:
```bash
pip install -r requirements.txt
```
4. **Run the application**
```bash
python3 main.py
```
Some features (e.g., lowering nice values) may require elevated privileges:
```bash
sudo python3 main.py
```

## Features

- **Real-time process retrieval** — Efficiently gathers live process information directly from the operating system.
- **Structured data pipeline** — Normalizes and formats raw system data for consistent UI consumption.
- **Multithreaded update engine** — Ensures smooth, non-blocking live updates using lightweight concurrency.
- **CPU monitoring** — Displays live CPU usage across all available cores.
- **Memory monitoring** — Tracks system memory usage, swap activity, and overall resource consumption.
- **Process page** — Provides detailed per-process information such as PID, CPU usage, memory usage, state, and TTY.
- **Signal-based process control** — Supports responsive and safe signalling mechanisms such as `SIGTERM` and `SIGKILL`.
- **Process termination (kill)** — Users can terminate running processes directly from the UI.
- **Adjust process priority (nice value)**  
  - Users can increase a process’s nice value (lower priority) without elevated privileges.  
  - Lowering the nice value (raising priority) requires elevated permissions (`sudo`).  
  - Non-root users are restricted by Linux to raising the nice value only and typically only once.
- **Backend–Frontend integration layer** — Bridges system-level data with the application interface for seamless interaction.

---

## Working Features

The following sections of the tool are fully implemented and functional:

- **CPU Page** — Real-time CPU load visualization.  
- **Memory Page** — Accurate system memory and swap tracking.  
- **Process Page** — Full process listing, live updates, process control, and priority adjustment.

These components form the current stable core of the system.

---

## Stretch Goals

Future enhancements planned for full-feature completion include:

- **Dashboard (Full Low-Level Reimplementation)**  
  Rebuild the dashboard using direct system calls and the Python `os` module for maximum accuracy and minimal overhead.
- **Disk Monitoring**  
  Track disk I/O usage, device throughput, read/write statistics, and filesystem usage.
- **Network Monitoring**  
  Monitor network interfaces, bandwidth, packet statistics, and connection states.

These goals will be integrated once the core functionality has matured.

---

## Purpose

The System Monitoring Tool's backend establishes a reliable foundation for:

- Accurate and immediate system insight.
- Efficient process management operations.
- Interactive and responsive user experiences.
- Future expansion of functionality across the entire application.
