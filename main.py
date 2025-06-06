import os
import time
from core.network_monitor import get_open_connections

def main():
    connections = get_open_connections(limit=10)
    print("Open network connections (max 10):")
    print("-" * 80)
    for conn in connections:
        print(f"{conn['laddr']:22} -> {conn['raddr']:22} | {conn['status']:<12} | {conn['process']} ({conn['pid']})")

if __name__ == "__main__":
    main()
