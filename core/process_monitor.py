import psutil

def get_top_processes(by="cpu", limit=5):
    """
    Returns a list of top `limit` processes sorted by 'cpu' or 'memory'.
    Each entry is a dict with pid, name, cpu%, and memory%.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            proc_info = proc.info
            processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    key = "cpu_percent" if by == "cpu" else "memory_percent"
    sorted_procs = sorted(processes, key=lambda p: p[key], reverse=True)
    return sorted_procs[:limit]
