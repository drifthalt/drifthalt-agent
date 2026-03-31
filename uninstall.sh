#!/bin/bash
set -e

echo "Uninstalling DriftHalt Agent..."

systemctl stop drifthalt-agent 2>/dev/null || true
systemctl disable drifthalt-agent 2>/dev/null || true

rm -f /etc/systemd/system/drifthalt-agent.service
rm -rf /opt/drifthalt-agent
rm -rf /etc/drifthalt

systemctl daemon-reload

echo "DriftHalt Agent uninstalled."