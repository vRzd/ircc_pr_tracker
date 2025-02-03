import requests
from src.logger import logger


class TelegramNotifier:
    def __init__(self, bot_token, enabled):
        self.bot_token = bot_token
        self.enabled = enabled

    def send_message(self, chat_ids, message):
        if not self.enabled:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        for chat_id in chat_ids:
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {chat_id}")
            else:
                logger.error(f"Failed to send message to {chat_id}: {response.status_code} - {response.text}")
