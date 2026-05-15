import subprocess
import json


def collect():
    """Collect PM2 process data via helper script."""
    processes = []

    try:
        result = subprocess.run(
            ['sudo', '-u', 'eber', '/usr/local/bin/drifthalt-pm2-info'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0 or not result.stdout.strip():
            return processes

        data = json.loads(result.stdout)
        for proc in data:
            processes.append({
                'name': proc.get('name'),
                'status': proc.get('pm2_env', {}).get('status'),
                'restart_count': proc.get('pm2_env', {}).get('restart_time', 0),
                'memory_mb': round(proc.get('monit', {}).get('memory', 0) / (1024 ** 2), 1),
                'pm_id': proc.get('pm_id'),
            })

    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass

    return processes