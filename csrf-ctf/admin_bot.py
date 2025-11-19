import hashlib
import sqlite3
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DATABASE = "users.db"


def visit_url(url):
    """Admin bot visits the reported URL"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(10)

        # Login as admin
        driver.get("http://localhost:5000/login")

        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys("admin")
        password_field.send_keys("admin_secret_password_123")

        password_field.submit()

        time.sleep(1)

        # Visit the reported URL
        driver.get(url)
        time.sleep(3)

    except Exception as e:
        print(f"Admin bot error: {e}")
    finally:
        if driver:
            driver.quit()
