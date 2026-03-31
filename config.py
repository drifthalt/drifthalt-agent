import os
import json

CONFIG_FILE = "/etc/drifthalt/agent.conf"
DEFAULT_SCAN_INTERVAL = 900  # 15 minutes in seconds

def load_config():
    """Load configuration from file or environment variables."""
    config = {
        "api_key": None,
        "api_url": "https://drifthalt.com",
        "scan_interval": DEFAULT_SCAN_INTERVAL,
        "auto_update": True,
        "server_id": None,
    }

    # Try config file first
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
        except (json.JSONDecodeError, IOError):
            pass

    # Environment variables override file config
    if os.environ.get("DRIFTHALT_API_KEY"):
        config["api_key"] = os.environ["DRIFTHALT_API_KEY"]
    if os.environ.get("DRIFTHALT_API_URL"):
        config["api_url"] = os.environ["DRIFTHALT_API_URL"]

    return config


def save_config(config):
    """Save configuration to file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)