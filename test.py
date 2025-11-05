#!/usr/bin/python3

import psutil

def list_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        processes.append(proc.info)
    return processes

print(list_processes())
