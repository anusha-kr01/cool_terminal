import datetime
import os
from core.process_monitor import get_top_processes
from core.network_monitor import get_open_connections
from core.system_info import get_system_info

LOG_DIR = "logs"

def save_to_file(title, content_lines):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{LOG_DIR}/{title}_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(content_lines))
    return filename

def log_summary():
    info = get_system_info()
    lines = ["System Summary", "-" * 40]
    for key, value in info.items():
        lines.append(f"{key}: {value}")
    return save_to_file("summary", lines)

def log_cpu():
    top_cpu = get_top_processes(by="cpu", limit=5)
    lines = ["Top 5 CPU-consuming processes", "-" * 40]
    for proc in top_cpu:
        lines.append(f"{proc['pid']} {proc['name']} CPU: {proc['cpu_percent']}% MEM: {proc['memory_percent']}%")
    return save_to_file("cpu", lines)

def log_memory():
    top_mem = get_top_processes(by="memory", limit=5)
    lines = ["Top 5 Memory-consuming processes", "-" * 40]
    for proc in top_mem:
        lines.append(f"{proc['pid']} {proc['name']} CPU: {proc['cpu_percent']}% MEM: {proc['memory_percent']}%")
    return save_to_file("memory", lines)

def log_network():
    connections = get_open_connections(limit=10)
    lines = ["Open Network Connections", "-" * 40]
    for conn in connections:
        laddr = str(conn['laddr']) if conn['laddr'] else "—"
        raddr = str(conn['raddr']) if conn['raddr'] else "—"
        status = conn['status']
        proc = f"{conn['process']} ({conn['pid']})"
        lines.append(f"{laddr} -> {raddr} | {status} | {proc}")
    return save_to_file("network", lines)
