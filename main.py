#!/usr/bin/env python3

import docker
import requests
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Telegram bot token
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")      # Telegram chat ID
JSON_URL = os.getenv("JSON_URL", "https://example.com/containers.json")
LOCAL_JSON_PATH = os.getenv("LOCAL_JSON_PATH", "containers.json")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # Convert to int, default 60s

# Initialize Docker client
try:
    client = docker.from_env()
except Exception as e:
    print(f"Error connecting to Docker daemon: {e}")
    exit(1)

def send_telegram_message(message):
    """Send a message via Telegram bot with explicit UTF-8 encoding."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot token or chat ID not set in .env. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # Explicitly encode the message to UTF-8 bytes, then decode back to string for JSON
    encoded_message = message.encode("utf-8").decode("utf-8")
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": encoded_message
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print(f"Telegram message sent: {message}")
    except requests.RequestException as e:
        print(f"Error sending Telegram message: {e}")

def fetch_container_names():
    """Fetch container names, preferring local JSON, falling back to online, notify on failure."""
    # Try local JSON first
    if os.path.exists(LOCAL_JSON_PATH):
        try:
            with open(LOCAL_JSON_PATH, 'r') as f:
                data = json.load(f)
                containers = data.get("containers", [])
                if containers:
                    print(f"Using local JSON file: {LOCAL_JSON_PATH}")
                    return containers
                else:
                    print(f"Local JSON file is empty or invalid, falling back to online.")
        except (json.JSONDecodeError, IOError) as e:
            error_msg = f"Error reading local JSON file '{LOCAL_JSON_PATH}': {e}"
            print(f"{error_msg}, falling back to online.")
            send_telegram_message(error_msg)

    # Fallback to online JSON
    try:
        response = requests.get(JSON_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        containers = data.get("containers", [])
        print(f"Using online JSON from: {JSON_URL}")
        return containers
    except requests.RequestException as e:
        error_msg = f"Error fetching online JSON file from '{JSON_URL}': {e}"
        print(error_msg)
        send_telegram_message(error_msg)
        return []

def check_container_health():
    """Check health of predefined containers and notify if unhealthy with 🔴."""
    container_names = fetch_container_names()
    if not container_names:
        print("No container names retrieved. Exiting check.")
        return

    for name in container_names:
        try:
            container = client.containers.get(name)
            health_status = container.attrs.get("State", {}).get("Health", {}).get("Status")
            container_status = container.attrs.get("State", {}).get("Status")

            # If no healthcheck is defined, rely on container status
            if health_status is None:
                if container_status != "running":
                    message = f"🔴 Container '{name}' is not running (Status: {container_status})"
                    send_telegram_message(message)
                continue

            # Check health status if HEALTHCHECK is defined
            if health_status == "unhealthy":
                message = f"🔴 UNHEALTHY Container '{name}'!"
                send_telegram_message(message)
            elif health_status == "healthy":
                print(f"Container '{name}' is healthy")
            else:
                print(f"Container '{name}' status: {health_status}")

        except docker.errors.NotFound:
            message = f"Container '{name}' not found on this host!"
            send_telegram_message(message)
        except docker.errors.APIError as e:
            print(f"Error checking container '{name}': {e}")

def main():
    print(f"Starting Docker health monitor. Checking every {CHECK_INTERVAL} seconds...")
    while True:
        check_container_health()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()