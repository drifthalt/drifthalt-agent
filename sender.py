import requests
import json
import logging

logger = logging.getLogger(__name__)


def register_server(api_url, api_key, system_info):
    """Register this server with the DriftHalt platform on first run."""
    try:
        response = requests.post(
            f"{api_url}/api/agent/register",
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            },
            json=system_info,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to register server: {e}")
        return None


def send_scan(api_url, api_key, payload):
    """Send a scan payload to the DriftHalt platform."""
    try:
        response = requests.post(
            f"{api_url}/api/agent/scan",
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send scan: {e}")
        return False