import subprocess
import os


def collect():
    """Collect system user information (metadata only — never passwords or keys)."""
    users = []

    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) < 7:
                    continue

                username = parts[0]
                uid = int(parts[2])
                shell = parts[6]

                # Skip system accounts (UID < 1000) except root
                if uid != 0 and uid < 1000:
                    continue

                # Skip accounts with no login shell
                if shell in ["/usr/sbin/nologin", "/bin/false", "/sbin/nologin"]:
                    continue

                has_sudo = _check_sudo(username)
                has_password = _check_has_password(username)
                has_ssh_key = _check_ssh_key(username, parts[5])

                users.append({
                    "username": username,
                    "has_sudo": has_sudo,
                    "has_password": has_password,
                    "has_ssh_key": has_ssh_key,
                })

    except Exception:
        pass

    return users


def _check_sudo(username):
    try:
        result = subprocess.run(
            ["groups", username],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return "sudo" in result.stdout.split()
    except Exception:
        return False


def _check_has_password(username):
    try:
        with open("/etc/shadow", "r") as f:
            for line in f:
                parts = line.split(":")
                if parts[0] == username:
                    password_field = parts[1]
                    return password_field not in ["!", "*", "!!"]
    except Exception:
        pass
    return False


def _check_ssh_key(username, home_dir):
    auth_keys = os.path.join(home_dir, ".ssh", "authorized_keys")
    try:
        return os.path.exists(auth_keys) and os.path.getsize(auth_keys) > 0
    except Exception:
        return False