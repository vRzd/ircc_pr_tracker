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

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

with open("./config.yaml", "r") as file:
    config = yaml.safe_load(file)

options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode
options.add_argument("--no-sandbox")  # Required in Docker
options.add_argument("--disable-dev-shm-usage")  # Prevents memory issues in Docker
options.add_argument("--disable-gpu")  # (Not needed for headless, but good practice)
options.add_argument("--remote-debugging-port=9222")  # Helps with debugging in Docker

driver = webdriver.Chrome(service=Service(config["webdriver_path"]), options=options)
driver.get(config["login_url"])


def send_telegram_message(chat_id, message, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": parse_mode}
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


def choosePrimaryApplicatnt():
    primary_applicant_app_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "full-app-link")))
    primary_applicant_app_link.click()


def get_activity_status():
    last_activity_status = ''
    try:
        background_check = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'chip-container')]//p[text()='In progress']"))).text
        last_activity_status += f"background check - {background_check.lower()}\n"

        activities = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "activity")))

        if activities:
            last_activity_raw = activities[0].find_element(By.CLASS_NAME, "date")
            last_activity_date = last_activity_raw.text.strip()
            last_activity_status += f"last app update - {last_activity_date}\n"
            return last_activity_status
    except Exception as e:
        print("Error retrieving last activity date:", e)
    return None


def get_processing_time():
    global avg_month
    try:
        driver.get(
            "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "wb-auto-24"))
        )

        dropdown1 = driver.find_element(By.ID, "wb-auto-24")
        dropdown1.click()
        option_economic = driver.find_element(By.CSS_SELECTOR, "#wb-auto-24 > option:nth-child(3)")
        option_economic.click()

        dropdown2 = driver.find_element(By.ID, "wb-auto-43")
        dropdown2.click()
        option_provincial = driver.find_element(By.CSS_SELECTOR, "#wb-auto-43 > option:nth-child(5)")
        option_provincial.click()

        dropdown3 = driver.find_element(By.ID, "wb-auto-46")
        dropdown3.click()
        option_no = driver.find_element(By.CSS_SELECTOR, "#wb-auto-46 > option:nth-child(3)")
        option_no.click()

        check_button = driver.find_element(By.CSS_SELECTOR, ".btn-call-to-action")
        check_button.click()

        avg_month = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "wb-auto-48"))).text

    except Exception as e:

        print("Error checking processing time:", e)
        return "avg processing time - is unavailable"
    finally:
        driver.close()
        return f"avg processing time - {avg_month}"


def generate_client_message(task_count, last_activity_status, processing_time):
    client_message = ''
    client_message += f"active task{'s' if task_count != 1 else ''} - {task_count}\n"
    client_message += last_activity_status
    client_message += processing_time
    print("Final message:", client_message)
    return  client_message


def send_message_to_recipients():
    for chat_id in config["chat_ids"]:
        send_telegram_message(chat_id, f"*OINP status*:\n{client_message}")

try:
    login()

    task_count = get_task_count()
    choosePrimaryApplicatnt()
    last_activity_status = get_activity_status()
    processing_time = get_processing_time()
    client_message = generate_client_message(task_count, last_activity_status, processing_time)
    send_message_to_recipients()


except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()
