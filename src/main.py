import yaml
import os
from src.logger import logger
from src.webdriver_manager import WebDriverManager
from src.telegram_notifier import TelegramNotifier
from src.pages.login_page import LoginPage
from src.pages.task_page import TaskPage
from src.pages.processing_time_page import ProcessingTimePage


class IRCCStatusChecker:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        self.config = self.load_config(config_path)
        self.driver_manager = WebDriverManager(self.config)
        self.notifier = TelegramNotifier(
            self.config["bot_token"], self.config["features"].get("report_to_telegram", False)
        )
        self.pages = {}
        self.initialize_pages()

    def initialize_pages(self):
        """Initialize only the pages required based on feature flags."""
        if self.config["features"].get("check_task_count", False):
            self.pages["login"] = LoginPage(self.driver_manager, self.config)
            self.pages["task"] = TaskPage(self.driver_manager)

        if self.config["features"].get("check_processing_time", False):
            self.pages["processing"] = ProcessingTimePage(self.driver_manager, self.config)

    def close_driver(self):
        self.driver_manager.close_driver()

    def run(self):
        try:
            task_count = 0
            processing_time = ""

            if "login" in self.pages and "task" in self.pages:
                self.pages["login"].login()
                task_count = self.pages["task"].get_task_count()

            if "processing" in self.pages:
                processing_time = self.pages["processing"].get_processing_time()

            client_message = f"active tasks - {task_count}\n{processing_time}"

            if self.config["features"].get("report_to_telegram", False):
                self.notifier.send_message(self.config.get("chat_ids", []), client_message)
        except Exception as e:
            logger.error("An error occurred:", exc_info=True)
        finally:
            self.close_driver()

    @staticmethod
    def load_config(config_path):
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

if __name__ == "__main__":
    checker = IRCCStatusChecker()
    checker.run()
