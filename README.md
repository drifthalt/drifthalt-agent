# DriftHalt Agent

The open-source monitoring agent for [DriftHalt](https://drifthalt.com) — a server intelligence platform that gives sysadmins and self-hosters a single dashboard into everything running across their servers.

The agent runs on each monitored server, collects system data every 15 minutes, and sends it to your DriftHalt dashboard over HTTPS. It is lightweight, read-only, and never accepts inbound connections.

---

## What It Collects

- **System info** — hostname, OS, kernel, uptime, architecture
- **Resource usage** — CPU, memory, and disk utilization
- **Installed packages** — name and version via apt/dpkg
- **Running services** — systemd service name and status
- **Docker containers** — container name, image, tag, and status
- **SSL certificates** — domain, issuer, and expiry date
- **Cron jobs** — schedule and command for each job
- **Open ports** — port number, protocol, and process
- **System users** — username, sudo access, SSH key presence

**The agent never collects:** passwords, SSH private keys, environment variables, file contents, or application data.

---

## Requirements

- Ubuntu 20.04+ or Debian 11+
- Python 3 (standard on most servers)
- sudo access to run the installer
- Outbound HTTPS access to drifthalt.com on port 443

---

## Installation

Create a free account at [drifthalt.com](https://drifthalt.com) to get your API key, then run:

```bash
curl -fsSL https://drifthalt.sh/install | sudo bash -s -- --api-key YOUR_API_KEY
```

Your server will appear in the dashboard within 15 minutes. Usually under a minute.

---

## Uninstallation

```bash
curl -fsSL https://raw.githubusercontent.com/drifthalt/drifthalt-agent/main/uninstall.sh | sudo bash
```

This removes the agent, systemd service, drifthalt user, and all local config files. Your data in the dashboard is not deleted automatically — remove the server from your dashboard separately if needed.

---

## Verify the Agent is Running

```bash
systemctl status drifthalt-agent
```

View live logs:

```bash
journalctl -u drifthalt-agent -f
```

---

## How It Works

The installer:
1. Creates a dedicated `drifthalt` system user with minimal permissions
2. Downloads and installs the agent to `/opt/drifthalt-agent`
3. Stores your API key in `/etc/drifthalt/agent.conf`
4. Creates a systemd service that runs on boot
5. Sends the first scan immediately

The agent runs every 15 minutes by default. Each scan collects system data and sends it as a JSON payload to the DriftHalt API over HTTPS. The agent is stateless — it does not store historical data locally.

---

## Security

- Agent runs as a dedicated `drifthalt` user with minimal permissions
- Communication is one-way outbound HTTPS only — no inbound connections
- Agent is read-only — it never writes, modifies, or executes anything on your server
- API key is stored in `/etc/drifthalt/agent.conf` with restricted permissions
- Full source code is available here for community audit

---

## Configuration

The agent config lives at `/etc/drifthalt/agent.conf`:

```json
{
  "api_key": "your_api_key",
  "api_url": "https://drifthalt.com",
  "scan_interval": 900,
  "auto_update": true
}
```

`scan_interval` is in seconds. Default is 900 (15 minutes).

After editing the config, restart the agent:

```bash
sudo systemctl restart drifthalt-agent
```

---

## Dashboard Features

Once your server is reporting data you can see:

- **Overview** — resource gauges, package count, service status summary
- **Packages** — every installed package and version, searchable
- **Services** — all systemd services with status filtering
- **SSL** — certificate expiry countdown with color-coded urgency
- **Cron** — all scheduled jobs across crontab and cron.d
- **History** — up to 50 past scans with a diff engine to compare any two

---

## Alerts

DriftHalt sends alerts via email, Slack, Discord, and generic webhooks for:

- Server offline or not responding
- SSL certificate expiring within 14 days
- Configuration drift detected between scans

Configure notification channels in your dashboard under Alerts.

---

## Contributing

Bug reports and feature requests are welcome via [GitHub Issues](https://github.com/drifthalt/drifthalt-agent/issues).

If you're reporting a bug, please include:
- Your OS and version (`lsb_release -a`)
- Agent version (`cat /opt/drifthalt-agent/agent.py | grep AGENT_VERSION`)
- Relevant logs (`journalctl -u drifthalt-agent -n 50`)

---

## License

MIT — see [LICENSE](LICENSE) for details.

The DriftHalt dashboard, API, and version intelligence engine are proprietary. The agent is open source.

---

## About

DriftHalt is operated by ELH Bridge LLC.

[drifthalt.com](https://drifthalt.com) · [feedback@drifthalt.com](mailto:feedback@drifthalt.com)
