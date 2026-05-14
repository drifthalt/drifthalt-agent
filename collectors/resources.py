import psutil

def collect():
    """Collect CPU, memory, and disk usage."""
    cpu_percent = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    disk_data = []
    for partition in psutil.disk_partitions():
        # Skip non-physical mounts
        if any(skip in partition.mountpoint for skip in ["/proc", "/sys", "/dev", "/run"]):
            continue
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_data.append({
                "mount": partition.mountpoint,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "percent": usage.percent,
            })
        except PermissionError:
            continue

    return {
        "cpu_percent": cpu_percent,
        "memory_total_mb": round(memory.total / (1024 ** 2)),
        "memory_used_mb": round(memory.used / (1024 ** 2)),
        "memory_percent": memory.percent,
        "swap_total_mb": round(swap.total / (1024 ** 2)),
        "swap_used_mb": round(swap.used / (1024 ** 2)),
        "swap_percent": swap.percent,
        "disk": disk_data,
    }