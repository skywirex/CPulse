#!/usr/bin/env python3

import time
from utilities import Utilities
from telegram_bot import TelegramBot
from docker import DockerClient
import json
import os


class CPluse:
    def __init__(self):
        # Load configuration from JSON file
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            print(f"Error: config.json not found at {config_path}")
            exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in config.json")
            exit(1)

        # Set configuration values from JSON
        self.TELEGRAM_BOT_TOKEN = config.get("telegram_bot_token")
        self.TELEGRAM_CHAT_ID = config.get("telegram_chat_id")
        self.JSON_URL = config.get("json_url", "https://example.com/containers.json")
        self.LOCAL_JSON_PATH = config.get("local_json_path", "containers.json")
        self.STATE_FILE = config.get("state_file", "container_states.json")
        self.CHECK_INTERVAL = int(config.get("check_interval", 60))

        # Validate required configurations
        if not self.TELEGRAM_BOT_TOKEN or not self.TELEGRAM_CHAT_ID:
            print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be specified in config.json")
            exit(1)

        try:
            self.client = DockerClient.from_env()
        except Exception as e:
            print(f"Error connecting to Docker daemon: {e}")
            exit(1)

        self.telegram_bot = TelegramBot(self.TELEGRAM_BOT_TOKEN, self.TELEGRAM_CHAT_ID)
        self.utilities = Utilities(
            self.JSON_URL,
            self.LOCAL_JSON_PATH,
            self.STATE_FILE,
            self.client,
            self.telegram_bot
        )

    def main(self):
        print(f"Starting Docker health monitor. Checking every {self.CHECK_INTERVAL} seconds...")
        self.utilities.check_container_health(first_run=True)
        while True:
            self.utilities.check_container_health()
            time.sleep(self.CHECK_INTERVAL)


if __name__ == "__main__":
    monitor = CPluse()
    monitor.main()