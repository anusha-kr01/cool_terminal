import psutil

def get_disk_usage():
    partitions = psutil.disk_partitions(all=False)
    usage_info = []
    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            usage_info.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            })
        except PermissionError:
            # Skip partitions that can't be accessed
            continue
    return usage_info
