import subprocess
import re
from datetime import datetime, timezone


def collect():
    """Collect last execution time for cron jobs from system journal."""
    executions = []

    try:
        result = subprocess.run(
            ['journalctl', '-u', 'cron', '--since', '24 hours ago',
             '--no-pager', '-q', '--output=short-iso'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0 or not result.stdout.strip():
            return executions

        # Parse CMD lines only
        pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})\s+'
            r'\S+\s+CRON\[\d+\]:\s+\((\w+)\)\s+CMD\s+\((.+)\)$'
        )

        seen = {}
        for line in result.stdout.splitlines():
            match = pattern.match(line)
            if not match:
                continue
            timestamp_str, user, command = match.groups()
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                ts_iso = timestamp.astimezone(timezone.utc).isoformat()
            except ValueError:
                continue

            key = f"{user}:{command}"
            if key not in seen or ts_iso > seen[key]['last_run']:
                seen[key] = {
                    'user': user,
                    'command': command,
                    'last_run': ts_iso,
                }

        executions = list(seen.values())

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return executions