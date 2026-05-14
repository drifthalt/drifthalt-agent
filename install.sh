#!/bin/bash
set -e

# DriftHalt Agent Installer
# Usage: curl -fsSL https://drifthalt.sh/install | sudo bash -s -- --api-key YOUR_KEY

AGENT_VERSION="1.2.1"
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
apt-get install -y -qq python3${PYTHON_VERSION}-venv 2>/dev/null || true

# Wait for apt lock to release
sleep 2

# Create agent user
if ! id "$AGENT_USER" &>/dev/null; then
  useradd --system --no-create-home --shell /usr/sbin/nologin "$AGENT_USER"
fi

# Add to docker group if Docker is installed
if getent group docker &>/dev/null; then
  usermod -aG docker "$AGENT_USER"
  echo "Docker detected — added $AGENT_USER to docker group"
fi

echo "$AGENT_USER ALL=(ALL) NOPASSWD: /usr/bin/crontab -l -u *" > /etc/sudoers.d/drifthalt-agent
chmod 440 /etc/sudoers.d/drifthalt-agent

# Download and install
mkdir -p "$INSTALL_DIR"
# Download and verify checksum
TARBALL="/tmp/drifthalt-agent-v${AGENT_VERSION}.tar.gz"
EXPECTED_CHECKSUM="4516237dcbd8897f4c7cffbb78f099ee117909e824158559301f15c6279b79a5"
rm -f "$TARBALL"
curl -fsSL "$REPO_URL" -o "$TARBALL"

ACTUAL_CHECKSUM=$(sha256sum "$TARBALL" | cut -d' ' -f1)
if [ "$ACTUAL_CHECKSUM" != "$EXPECTED_CHECKSUM" ]; then
  echo "Error: Checksum verification failed. The downloaded file may be corrupted or tampered with."
  echo "Expected: $EXPECTED_CHECKSUM"
  echo "Got:      $ACTUAL_CHECKSUM"
  rm -f "$TARBALL"
  exit 1
fi

echo "Checksum verified."
tar -xz -C "$INSTALL_DIR" --strip-components=1 -f "$TARBALL"
rm -f "$TARBALL"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR" || python3 -m venv --without-pip "$VENV_DIR"

# Install pip if missing
if [ ! -f "$VENV_DIR/bin/pip" ]; then
  curl -fsSL https://bootstrap.pypa.io/get-pip.py | "$VENV_DIR/bin/python3"
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -q --upgrade pip
"$VENV_DIR/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

# Create config
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_DIR/agent.conf" << EOF
{
  "api_key": "${API_KEY}",
  "api_url": "${API_URL}",
  "scan_interval": 900
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