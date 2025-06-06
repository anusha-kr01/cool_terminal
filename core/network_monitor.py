import psutil

def get_open_connections(limit=10):
    """
    Returns a list of active network connections with their PID and process name.
    """
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status != psutil.CONN_LISTEN and not conn.raddr:
            continue  # Skip irrelevant connections

        try:
            proc = psutil.Process(conn.pid) if conn.pid else None
            name = proc.name() if proc else "System"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            name = "Unknown"

        connections.append({
            "laddr": f"{conn.laddr.ip}:{conn.laddr.port}",
            "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "—",
            "status": conn.status,
            "pid": conn.pid,
            "process": name
        })

    return connections[:limit]
