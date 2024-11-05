import os
import yaml
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

with open("./config.yaml", "r") as file:
    config = yaml.safe_load(file)

driver = webdriver.Firefox(service=Service(config["webdriver_path"]))
driver.get(config["login_url"])

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent successfully to", chat_id)
    else:
        print(f"Failed to send message to {chat_id}: {response.status_code} - {response.text}")


def login():
    try:
        uci_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "uci"))
        )
        password_input = driver.find_element(By.ID, "password")
        uci_input.send_keys(config["uci"])
        password_input.send_keys(config["password"])
        password_input.send_keys(Keys.RETURN)
    except Exception as e:
        print("Login failed:", e)


def get_task_count():
    current_task_count = 0
    try:
        task_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "apps-task"))
        )
        for element in task_elements:
            task_text = element.text.strip()
            try:
                current_task_count += int(task_text.split()[0])
            except (ValueError, IndexError):
                print(f"Error parsing task text: '{task_text}'")
    except Exception as e:
        print("Error retrieving tasks:", e)
        return None
    return current_task_count


def get_last_activity_date():
    try:
        activities = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "activity")))
        if activities:
            last_activity_raw = activities[0].find_element(By.CLASS_NAME, "date")
            return last_activity_raw.text.strip()
    except Exception as e:
        print("Error retrieving last activity date:", e)
    return None



try:
    login()

    task_count = get_task_count()
    message = f"{task_count} task{'s' if task_count != 1 else ''}"

    primary_applicant_app_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "full-app-link")))
    primary_applicant_app_link.click()

    last_activity_date = get_last_activity_date()
    if last_activity_date:
        message += f", last update: {last_activity_date}"

    print("Final message:", message)

    for chat_id in config["chat_ids"]:
        send_telegram_message(chat_id, f"PR app status: {message} - але все буде чікі-пікі!")

except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()
