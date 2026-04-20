#!/usr/bin/env python3
"""
DriftHalt Agent — System data collector
https://github.com/drifthalt/drifthalt-agent
License: MIT
"""

import sys
import time
import logging
import argparse
from datetime import datetime, timezone

from config import load_config, save_config
from sender import register_server, send_scan
from collectors import system, resources, packages, services, docker, ssl, cron, ports, users

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

AGENT_VERSION = "1.0.4"


def collect_all():
    """Run all collectors and return the full payload."""
    logger.info("Starting data collection...")

    payload = {
        "agent_version": AGENT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": system.collect(),
        "resources": resources.collect(),
        "packages": packages.collect(),
        "docker_containers": docker.collect(),
        "services": services.collect(),
        "ssl_certificates": ssl.collect(),
        "cron_jobs": cron.collect(),
        "open_ports": ports.collect(),
        "users": users.collect(),
    }

    logger.info(
        f"Collection complete — "
        f"{len(payload['packages'])} packages, "
        f"{len(payload['services'])} services, "
        f"{len(payload['docker_containers'])} containers"
    )

    return payload


def ensure_registered(config):
    """Register the server if we don't have a server_id yet."""
    if config.get("server_id"):
        return config

    logger.info("First run — registering server...")
    system_info = system.collect()

    result = register_server(config["api_url"], config["api_key"], system_info)

    if result and result.get("server_id"):
        config["server_id"] = result["server_id"]
        save_config(config)
        logger.info(f"Server registered with ID: {config['server_id']}")
    else:
        logger.error("Failed to register server. Will retry on next run.")

    return config


def run_once(config):
    """Run a single scan cycle."""
    config = ensure_registered(config)

    if not config.get("server_id"):
        logger.error("Not registered — skipping scan.")
        return False

    payload = collect_all()
    payload["server_id"] = config["server_id"]

    success = send_scan(config["api_url"], config["api_key"], payload)

    if success:
        logger.info("Scan sent successfully.")
    else:
        logger.warning("Scan failed to send — will retry next cycle.")

    return success


def run_loop(config):
    """Run continuously on a timer."""
    interval = config.get("scan_interval", 900)
    logger.info(f"Starting agent — scan interval: {interval}s")

    while True:
        try:
            run_once(config)
        except Exception as e:
            logger.error(f"Unexpected error during scan: {e}")

        logger.info(f"Next scan in {interval} seconds.")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="DriftHalt Agent")
    parser.add_argument("--once", action="store_true", help="Run one scan and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config = load_config()

    if not config.get("api_key"):
        logger.error("No API key configured. Set DRIFTHALT_API_KEY or add to config file.")
        sys.exit(1)

    if args.once:
        success = run_once(config)
        sys.exit(0 if success else 1)
    else:
        run_loop(config)


if __name__ == "__main__":
    main()