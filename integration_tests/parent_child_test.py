#!/usr/bin/env python3
"""
parent_child_test.py - Test parent-child process relationships
Creates a process hierarchy to test PPID column
"""
import os
import time
import sys
from multiprocessing import Process

def grandchild_worker(name):
    """Grandchild process - does CPU work"""
    try:
        counter = 0
        while True:
            for i in range(100000):
                counter += i * i
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass

def child_worker(child_id, num_grandchildren):
    """Child process - spawns grandchildren and does CPU work"""
    # Spawn grandchildren
    grandchildren = []
    for i in range(num_grandchildren):
        p = Process(target=grandchild_worker, args=(f"GC-{child_id}.{i+1}",))
        p.start()
        grandchildren.append(p)
        time.sleep(0.2)
    
    # Do CPU work
    try:
        counter = 0
        while True:
            for i in range(100000):
                counter += i * i
            time.sleep(0.05)
    except KeyboardInterrupt:
        # Cleanup grandchildren
        for p in grandchildren:
            p.terminate()
            p.join(timeout=1)

def main():
    """Parent process - spawns children"""
    num_children = 3
    grandchildren_per_child = 2
    
    # Spawn children
    children = []
    for i in range(num_children):
        p = Process(target=child_worker, args=(i+1, grandchildren_per_child))
        p.start()
        children.append(p)
        time.sleep(0.3)
    
    # Parent does CPU work
    try:
        counter = 0
        while True:
            for i in range(100000):
                counter += i * i
            time.sleep(0.05)
    except KeyboardInterrupt:
        # Cleanup children
        for p in children:
            p.terminate()
            p.join(timeout=2)

if __name__ == "__main__":
    main()
