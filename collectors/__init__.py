import platform
import socket
import subprocess
import time


def collect():
    """Collect basic system information."""
    try:
        uptime_seconds = int(time.time() - _get_boot_time())
    except Exception:
        uptime_seconds = 0

    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": _get_os_version(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "uptime_seconds": uptime_seconds,
    }


def _get_boot_time():
    try:
        import psutil
        return psutil.boot_time()
    except Exception:
        with open("/proc/uptime", "r") as f:
            uptime = float(f.read().split()[0])
            return time.time() - uptime


def _get_os_version():
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return platform.version()