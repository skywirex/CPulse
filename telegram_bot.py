import requests

class TelegramBot:
    def __init__(self, bot_token, chat_id):
        self.TELEGRAM_BOT_TOKEN = bot_token
        self.TELEGRAM_CHAT_ID = chat_id

    def send_telegram_message(self, message):
        """Send a message via Telegram bot with explicit UTF-8 encoding."""
        if not self.TELEGRAM_BOT_TOKEN or not self.TELEGRAM_CHAT_ID:
            print("Telegram bot token or chat ID not set in .env. Skipping notification.")
            return

        url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
        encoded_message = message.encode("utf-8").decode("utf-8")
        payload = {"chat_id": self.TELEGRAM_CHAT_ID, "text": encoded_message}
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            print(f"Telegram message sent: {message}")
        except requests.RequestException as e:
            print(f"Error sending Telegram message: {e}")