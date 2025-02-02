import os
import requests
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from contextlib import contextmanager


@contextmanager
def selenium_driver(config):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=Service(config["webdriver_path"]), options=options)
    try:
        yield driver
    finally:
        driver.quit()


class IRCCStatusChecker:
    def __init__(self, config_path="./config.yaml"):
        self.load_config(config_path)

    def load_config(self, config_path):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def send_telegram_message(self, chat_id, message, parse_mode="Markdown"):
        url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": parse_mode}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Message sent successfully to {chat_id}")
        else:
            print(f"Failed to send message to {chat_id}: {response.status_code} - {response.text}")

    def login(self, driver):
        try:
            driver.get(self.config["login_url"])
            uci_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "uci"))
            )
            password_input = driver.find_element(By.ID, "password")
            uci_input.send_keys(self.config["uci"])
            password_input.send_keys(self.config["password"])
            password_input.send_keys(Keys.RETURN)
        except Exception as e:
            print("Login failed:", e)

    def get_task_count(self, driver):
        try:
            task_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "apps-task"))
            )
            return sum(int(task.text.split()[0]) for task in task_elements if task.text.strip().isdigit())
        except Exception as e:
            print("Error retrieving tasks:", e)
            return 0

    def choose_primary_applicant(self, driver):
        try:
            primary_applicant_app_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "full-app-link"))
            )
            primary_applicant_app_link.click()
        except Exception as e:
            print("Error choosing primary applicant:", e)

    def get_activity_status(self, driver):
        last_activity_status = ""
        try:
            background_check = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'chip-container')]//p[text()='In progress']")
                )
            ).text
            last_activity_status += f"background check - {background_check.lower()}\n"

            activities = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "activity"))
            )

            if activities:
                last_activity_raw = activities[0].find_element(By.CLASS_NAME, "date")
                last_activity_date = last_activity_raw.text.strip()
                last_activity_status += f"last app update - {last_activity_date}\n"
        except Exception as e:
            print("Error retrieving last activity date:", e)
        return last_activity_status

    def get_processing_time(self, driver):
        try:
            driver.get(
                "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html"
            )

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "wb-auto-24"))
            )

            driver.find_element(By.ID, "wb-auto-24").click()
            driver.find_element(By.CSS_SELECTOR, "#wb-auto-24 > option:nth-child(3)").click()

            driver.find_element(By.ID, "wb-auto-43").click()
            driver.find_element(By.CSS_SELECTOR, "#wb-auto-43 > option:nth-child(5)").click()

            driver.find_element(By.ID, "wb-auto-46").click()
            driver.find_element(By.CSS_SELECTOR, "#wb-auto-46 > option:nth-child(3)").click()

            driver.find_element(By.CSS_SELECTOR, ".btn-call-to-action").click()

            avg_month = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "wb-auto-48"))
            ).text
            return f"avg processing time - {avg_month}"
        except Exception as e:
            print("Error checking processing time:", e)
            return "avg processing time - is unavailable"

    def run(self):
        with selenium_driver(self.config) as driver:
            try:
                self.login(driver)
                task_count = self.get_task_count(driver)
                self.choose_primary_applicant(driver)
                last_activity_status = self.get_activity_status(driver)
                processing_time = self.get_processing_time(driver)
                client_message = f"active tasks - {task_count}\n{last_activity_status}{processing_time}"
                for chat_id in self.config["chat_ids"]:
                    self.send_telegram_message(chat_id, f"*IRCC status*:\n{client_message}")
            except Exception as e:
                print("An error occurred:", e)


if __name__ == "__main__":
    checker = IRCCStatusChecker()
    checker.run()
