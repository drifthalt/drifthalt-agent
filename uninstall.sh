#!/bin/bash
set -e

# DriftHalt Agent Uninstaller
# Usage: sudo bash uninstall.sh

if [[ $EUID -ne 0 ]]; then
  echo "Error: This script must be run as root (use sudo)."
  exit 1
fi

echo "Uninstalling DriftHalt Agent..."

systemctl stop drifthalt-agent 2>/dev/null || true
systemctl disable drifthalt-agent 2>/dev/null || true
rm -f /etc/systemd/system/drifthalt-agent.service
rm -rf /opt/drifthalt-agent
rm -rf /etc/drifthalt
rm -f /etc/sudoers.d/drifthalt-agent
userdel drifthalt 2>/dev/null || true
systemctl daemon-reload

echo ""
echo "DriftHalt Agent uninstalled."
echo "Remember to delete this server from your dashboard at https://drifthalt.com/dashboard"