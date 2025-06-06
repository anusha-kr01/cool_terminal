import platform
import psutil
import time
from datetime import datetime

def get_system_info():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)

    return {
        "OS": f"{platform.system()} {platform.release()}",
        "Architecture": platform.machine(),
        "CPU Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True),
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Used Memory (GB)": round(psutil.virtual_memory().used / (1024 ** 3), 2),
        "Uptime": f"{uptime_hours}h {uptime_minutes}m",
        "Boot Time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Running Processes": len(psutil.pids())
    }
