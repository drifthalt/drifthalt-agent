import subprocess


def collect():
    """Collect open listening ports."""
    ports = []

    try:
        result = subprocess.run(
            ["ss", "-tlnup"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        for line in result.stdout.split("\n")[1:]:  # Skip header
            parts = line.split()
            if len(parts) < 5:
                continue

            local_addr = parts[3]
            process_info = parts[-1] if len(parts) > 5 else ""

            # Parse port from address like 0.0.0.0:22 or *:80
            if ":" in local_addr:
                port_str = local_addr.rsplit(":", 1)[-1]
                try:
                    port = int(port_str)
                except ValueError:
                    continue
            else:
                continue

            # Extract process name
            process = "unknown"
            if 'users:((' in process_info:
                try:
                    proc_part = process_info.split('users:((')[1]
                    process = proc_part.split('"')[1]
                except Exception:
                    pass

            protocol = "tcp"

            # Avoid duplicates
            if not any(p["port"] == port for p in ports):
                ports.append({
                    "port": port,
                    "protocol": protocol,
                    "process": process,
                })

    except Exception:
        pass

    return sorted(ports, key=lambda x: x["port"])