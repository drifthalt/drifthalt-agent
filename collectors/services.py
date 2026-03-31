import subprocess


def collect():
    """Collect systemd service status."""
    services = []

    try:
        result = subprocess.run(
            [
                "systemctl", "list-units",
                "--type=service",
                "--all",
                "--no-pager",
                "--no-legend",
                "--plain",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) < 4:
                continue

            name = parts[0].replace(".service", "")
            load = parts[1]
            active = parts[2]
            sub = parts[3]

            if load != "loaded":
                continue

            status = _map_status(active, sub)

            # Check if enabled
            enabled = False
            try:
                check = subprocess.run(
                    ["systemctl", "is-enabled", parts[0]],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                enabled = check.stdout.strip() == "enabled"
            except Exception:
                pass

            services.append({
                "name": name,
                "status": status,
                "enabled": enabled,
                "type": "systemd",
            })

    except Exception:
        pass

    return services


def _map_status(active, sub):
    if active == "active" and sub == "running":
        return "running"
    elif active == "failed":
        return "failed"
    elif active == "inactive":
        return "inactive"
    else:
        return "stopped"