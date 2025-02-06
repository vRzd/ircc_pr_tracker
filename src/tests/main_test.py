import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from src.main import IRCCStatusChecker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

class TestIRCCStatusChecker(unittest.TestCase):

    @patch("src.main.yaml.safe_load")
    @patch("src.webdriver_manager_c.WebDriverManager")
    @patch("src.telegram_notifier.TelegramNotifier")
    @patch("selenium.webdriver.Chrome")
    def setUp(self, mock_selenium, mock_notifier, mock_web_driver, mock_yaml_load):
        self.mock_config = {
            "bot_token": "test_token",
            "chat_ids": ["1234567"],
            "login_url": "https://ircc-tracker-suivi.apps.cic.gc.ca/en/login",
            "processing_time_url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html",
            "uci": "123456789",
            "password": "test_password",
            "webdriver": {
                "headless": True
            },
            "features": {
                "check_task_count": True,
                "check_processing_time": True,
                "report_to_telegram": False
            }
        }
        mock_yaml_load.return_value = self.mock_config
        self.checker = IRCCStatusChecker(os.path.join(os.path.dirname(__file__), "../config.yaml"))

    def test_initialize_pages(self):
        self.assertIn("login", self.checker.pages)
        self.assertIn("task", self.checker.pages)
        self.assertIn("processing", self.checker.pages)

    @patch("src.pages.processing_time_page.ProcessingTimePage")
    @patch("src.pages.task_page.TaskPage")
    @patch("src.pages.login_page.LoginPage")
    @patch("selenium.webdriver.Chrome")
    def test_run(self, mock_selenium, mock_processing_time_page, mock_task_page, mock_login_page):
        mock_login_page = mock_login_page.return_value
        mock_task_page = mock_task_page.return_value
        mock_processing_page = mock_processing_time_page.return_value

        mock_login_page.login.return_value = None
        mock_task_page.get_task_count.return_value = 5
        mock_processing_page.get_processing_time.return_value = "Processing time: 30 days"

        self.checker.pages["login"] = mock_login_page
        self.checker.pages["task"] = mock_task_page
        self.checker.pages["processing"] = mock_processing_page

        with patch("src.logger.logger.error") as mock_logger:
            self.checker.run()

            mock_login_page.login.assert_called_once()
            mock_task_page.get_task_count.assert_called_once()
            mock_processing_page.get_processing_time.assert_called_once()
            mock_logger.assert_not_called()

    @patch("src.webdriver_manager_c.WebDriverManager.close_driver")
    def test_close_driver(self, mock_close_driver):
        self.checker.close_driver()
        mock_close_driver.assert_called_once()

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="bot_token: test_token")
    @patch("src.main.yaml.safe_load")
    def test_load_config(self, mock_yaml_load, mock_open):
        mock_yaml_load.return_value = {"bot_token": "test_token"}
        config = IRCCStatusChecker.load_config("dummy_path.yaml")
        self.assertEqual(config["bot_token"], "test_token")
        mock_open.assert_called_once_with("dummy_path.yaml", "r")
        mock_yaml_load.assert_called_once()


if __name__ == "__main__":
    unittest.main()
