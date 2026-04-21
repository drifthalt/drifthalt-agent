#!/bin/bash
set -e

# DriftHalt Agent Installer
# Usage: curl -fsSL https://drifthalt.sh/install | sudo bash -s -- --api-key YOUR_KEY

AGENT_VERSION="1.1.6"
AGENT_USER="drifthalt"
INSTALL_DIR="/opt/drifthalt-agent"
VENV_DIR="/opt/drifthalt-agent/venv"
CONFIG_DIR="/etc/drifthalt"
SERVICE_FILE="/etc/systemd/system/drifthalt-agent.service"
REPO_URL="https://github.com/drifthalt/drifthalt-agent/archive/refs/tags/v${AGENT_VERSION}.tar.gz"

# Parse arguments
API_KEY=""
API_URL="https://drifthalt.com"
while [[ $# -gt 0 ]]; do
  case $1 in
    --api-key) API_KEY="$2"; shift 2 ;;
    --api-url) API_URL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$API_KEY" ]; then
  echo "Error: --api-key is required"
  echo "Usage: curl -fsSL https://drifthalt.sh/install | sudo bash -s -- --api-key YOUR_KEY"
  exit 1
fi

echo "Installing DriftHalt Agent v${AGENT_VERSION}..."

# Check for Python 3
if ! command -v python3 &>/dev/null; then
  echo "Installing Python 3..."
  apt-get update -qq && apt-get install -y -qq python3
fi

# Install python3-venv
echo "Installing python3-venv..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
apt-get update -qq 2>/dev/null
apt-get install -y -qq python3-venv 2>/dev/null || true

# Wait for apt lock to release
sleep 5

# Create agent user
if ! id "$AGENT_USER" &>/dev/null; then
  useradd --system --no-create-home --shell /usr/sbin/nologin "$AGENT_USER"
fi

echo "$AGENT_USER ALL=(ALL) NOPASSWD: /usr/bin/crontab -l -u *" > /etc/sudoers.d/drifthalt-agent
chmod 440 /etc/sudoers.d/drifthalt-agent

# Download and install
mkdir -p "$INSTALL_DIR"
curl -fsSL "$REPO_URL" | tar -xz -C "$INSTALL_DIR" --strip-components=1

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR" || python3 -m venv --without-pip "$VENV_DIR"

# Install pip if missing
if [ ! -f "$VENV_DIR/bin/pip" ]; then
  curl -fsSL https://bootstrap.pypa.io/get-pip.py | "$VENV_DIR/bin/python3"
fi

# Install Python dependencies into venv
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

# Create config
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_DIR/agent.conf" << EOF
{
  "api_key": "${API_KEY}",
  "api_url": "${API_URL}",
  "scan_interval": 900,
  "auto_update": true
}
EOF
chmod 640 "$CONFIG_DIR/agent.conf"
chown $AGENT_USER:$AGENT_USER "$CONFIG_DIR/agent.conf"

# Create systemd service
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=DriftHalt Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${AGENT_USER}
ExecStart=${VENV_DIR}/bin/python ${INSTALL_DIR}/agent.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable drifthalt-agent
systemctl restart drifthalt-agent

echo ""
echo "DriftHalt Agent installed and running."
echo "Check status: systemctl status drifthalt-agent"
echo "View logs:    journalctl -u drifthalt-agent -f"