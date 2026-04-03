import subprocess
import os


def collect():
    """Collect cron jobs from crontab and /etc/cron.d/"""
    cron_jobs = []

    # System users to check
    users = _get_system_users()

    for user in users:
        jobs = _get_user_crontab(user)
        cron_jobs.extend(jobs)

    # /etc/cron.d/ directory
    jobs = _get_cron_d()
    cron_jobs.extend(jobs)

    return cron_jobs


def _get_system_users():
    users = []
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) >= 7:
                    username = parts[0]
                    shell = parts[6].strip()
                    # Only users with real shells
                    if shell not in ["/usr/sbin/nologin", "/bin/false", "/sbin/nologin"]:
                        users.append(username)
    except Exception:
        users = ["root"]
    return users


def _get_user_crontab(user):
    jobs = []
    try:
        result = subprocess.run(
            ["sudo","crontab", "-l", "-u", user],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split(None, 5)
                if len(parts) >= 6:
                    schedule = " ".join(parts[:5])
                    command = parts[5]
                    jobs.append({
                        "user": user,
                        "schedule": schedule,
                        "command": command,
                        "source": "crontab",
                    })
    except Exception:
        pass
    return jobs


def _get_cron_d():
    jobs = []
    cron_d = "/etc/cron.d"
    try:
        for filename in os.listdir(cron_d):
            filepath = os.path.join(cron_d, filename)
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split(None, 6)
                        if len(parts) >= 7:
                            schedule = " ".join(parts[:5])
                            user = parts[5]
                            command = parts[6]
                            jobs.append({
                                "user": user,
                                "schedule": schedule,
                                "command": command,
                                "source": "cron_d",
                            })
    except Exception:
        pass
    return jobs