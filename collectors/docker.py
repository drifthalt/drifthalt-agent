import subprocess
import json


def collect():
    """Collect Docker container information."""
    containers = []

    # Check if Docker is available
    try:
        subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
            check=True,
        )
    except Exception:
        return containers  # Docker not available, skip silently

    try:
        result = subprocess.run(
            [
                "docker", "ps", "-a",
                "--format",
                '{"name":"{{.Names}}","image":"{{.Image}}","status":"{{.Status}}","ports":"{{.Ports}}"}',
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                c = json.loads(line)
                image_parts = c["image"].rsplit(":", 1)
                image_name = image_parts[0]
                image_tag = image_parts[1] if len(image_parts) > 1 else "latest"

                status = "running" if c["status"].startswith("Up") else "stopped"

                containers.append({
                    "name": c["name"],
                    "image": image_name,
                    "tag": image_tag,
                    "status": status,
                    "ports": [c["ports"]] if c["ports"] else [],
                })
            except Exception:
                continue

    except Exception:
        pass

    return containers