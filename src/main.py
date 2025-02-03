import os
import requests
import yaml
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class IRCCStatusChecker:
    def __init__(self, config_path="./config.yaml"):
        self.load_config(config_path)
        self.setup_driver()

    def load_config(self, config_path):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(service=Service(self.config["webdriver_path"]), options=options)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def send_telegram_message(self, chat_id, message, parse_mode="Markdown"):
        if not self.config.get("features", {}).get("report_to_telegram", False):
            return

        url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": parse_mode}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info(f"Message sent successfully to {chat_id}")
        else:
            logging.error(f"Failed to send message to {chat_id}: {response.status_code} - {response.text}")

    def login(self):
        try:
            self.driver.get(self.config["login_url"])
            uci_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "uci"))
            )
            password_input = self.driver.find_element(By.ID, "password")
            uci_input.send_keys(self.config["uci"])
            password_input.send_keys(self.config["password"])
            password_input.send_keys(Keys.RETURN)
            logging.info("Login successful.")
        except Exception as e:
            logging.error("Login failed:", exc_info=True)

    def get_task_count(self):
        if not self.config.get("features", {}).get("check_task_count", False):
            return 0

        try:
            task_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "apps-task"))
            )
            task_count = sum(int(task.text.split()[0]) for task in task_elements if task.text.strip().isdigit())
            logging.info(f"Task count retrieved: {task_count}")
            return task_count
        except Exception as e:
            logging.error("Error retrieving tasks:", exc_info=True)
            return 0

    def get_processing_time(self):
        if not self.config.get("features", {}).get("check_processing_time", False):
            return ""

        try:
            self.driver.get(
                "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html"
            )

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "wb-auto-24"))
            )

            dropdown1 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "wb-auto-24")))
            dropdown1.click()
            self.driver.find_element(By.CSS_SELECTOR, "#wb-auto-24 > option:nth-child(3)").click()

            dropdown2 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "wb-auto-43")))
            dropdown2.click()
            self.driver.find_element(By.CSS_SELECTOR, "#wb-auto-43 > option:nth-child(5)").click()

            dropdown3 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "wb-auto-46")))
            dropdown3.click()
            self.driver.find_element(By.CSS_SELECTOR, "#wb-auto-46 > option:nth-child(3)").click()

            self.driver.find_element(By.CSS_SELECTOR, ".btn-call-to-action").click()

            avg_month = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "wb-auto-48"))
            ).text
            logging.info(f"Processing time retrieved: {avg_month}")
            return f"avg processing time - {avg_month}"
        except Exception as e:
            logging.error("Error checking processing time:", exc_info=True)
            return "avg processing time - is unavailable"

    def run(self):
        try:
            self.login()
            task_count = self.get_task_count()
            processing_time = self.get_processing_time()
            client_message = f"active tasks - {task_count}\n{processing_time}"

            if self.config.get("features", {}).get("report_to_telegram", False):
                for chat_id in self.config.get("chat_ids", []):
                    self.send_telegram_message(chat_id, f"*IRCC status*:\n{client_message}")
        except Exception as e:
            logging.error("An error occurred:", exc_info=True)
        finally:
            self.close_driver()


if __name__ == "__main__":
    checker = IRCCStatusChecker()
    checker.run()
