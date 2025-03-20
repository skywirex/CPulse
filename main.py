#!/usr/bin/env python3

import time
from utilities import Utilities
from telegram_bot import TelegramBot
from docker import DockerClient
from dotenv import load_dotenv
import os


class CPluse:  # Renamed from DockerHealthMonitor
    def __init__ ( self ):
        load_dotenv ()
        self.TELEGRAM_BOT_TOKEN = os.getenv ( "TELEGRAM_BOT_TOKEN" )
        self.TELEGRAM_CHAT_ID = os.getenv ( "TELEGRAM_CHAT_ID" )
        self.JSON_URL = os.getenv ( "JSON_URL", "https://example.com/containers.json" )
        self.LOCAL_JSON_PATH = os.getenv ( "LOCAL_JSON_PATH", "containers.json" )
        self.STATE_FILE = os.getenv ( "STATE_FILE", "container_states.json" )
        self.CHECK_INTERVAL = int ( os.getenv ( "CHECK_INTERVAL", 60 ) )

        try:
            self.client = DockerClient.from_env ()
        except Exception as e:
            print ( f"Error connecting to Docker daemon: {e}" )
            exit ( 1 )

        self.telegram_bot = TelegramBot ( self.TELEGRAM_BOT_TOKEN, self.TELEGRAM_CHAT_ID )
        self.utilities = Utilities (
            self.JSON_URL,
            self.LOCAL_JSON_PATH,
            self.STATE_FILE,
            self.client,
            self.telegram_bot
        )

    def main ( self ):
        print ( f"Starting Docker health monitor. Checking every {self.CHECK_INTERVAL} seconds..." )
        self.utilities.check_container_health ( first_run=True )
        while True:
            self.utilities.check_container_health ()
            time.sleep ( self.CHECK_INTERVAL )


if __name__ == "__main__":
    monitor = CPluse ()  # Updated to use new class name
    monitor.main ()