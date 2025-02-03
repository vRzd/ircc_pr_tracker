# telegram_client.py
import requests


class TelegramClient:

    def __init__(self, bot_token):
        self.bot_token = bot_token

    def send_message(self, chat_id, message, parse_mode="Markdown"):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode
        }

        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Message sent successfully to chat_id={chat_id}")
        else:
            print(f"Failed to send message to {chat_id}: {response.status_code} - {response.text}")
