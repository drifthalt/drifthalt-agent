import subprocess
import re


def collect():
    """Detect OOM kill events from kernel logs in the last 24 hours."""
    events = []

    try:
        result = subprocess.run(
            ['journalctl', '-k', '--since', '24 hours ago', '--no-pager', '-q'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            events = _parse_oom_lines(result.stdout.splitlines())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return events


def _parse_oom_lines(lines):
    events = []
    pattern = re.compile(
        r'Out of memory.*?Kill(?:ed)? process (\d+) \(([^)]+)\)',
        re.IGNORECASE
    )

    for line in lines:
        if 'out of memory' not in line.lower():
            continue
        match = pattern.search(line)
        if match:
            events.append({
                'pid': match.group(1),
                'process': match.group(2),
                'raw': line.strip()[:200],
            })

    return events