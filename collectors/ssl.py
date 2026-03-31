import ssl
import socket
import subprocess
from datetime import datetime, timezone


def collect():
    """Collect SSL certificate information from Nginx/Apache configs and check expiry."""
    certs = []
    domains = _find_domains()

    for domain in domains:
        cert_info = _check_cert(domain)
        if cert_info:
            certs.append(cert_info)

    return certs


def _find_domains():
    """Find domains from Nginx config."""
    domains = set()

    try:
        result = subprocess.run(
            ["grep", "-r", "server_name", "/etc/nginx/sites-enabled/"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in result.stdout.split("\n"):
            if "server_name" in line:
                parts = line.strip().split()
                for part in parts[1:]:
                    part = part.rstrip(";")
                    if "." in part and not part.startswith("_"):
                        domains.add(part)
    except Exception:
        pass

    return list(domains)


def _check_cert(domain):
    """Check SSL certificate for a domain."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

        expires_str = cert["notAfter"]
        expires_at = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
        expires_at = expires_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        days_remaining = (expires_at - now).days

        issuer = dict(x[0] for x in cert.get("issuer", []))
        issuer_name = issuer.get("organizationName", "Unknown")

        return {
            "domain": domain,
            "issuer": issuer_name,
            "expires_at": expires_at.isoformat(),
            "days_remaining": days_remaining,
        }

    except Exception:
        return None