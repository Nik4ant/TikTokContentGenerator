import os
import json

from app.logger_module import logger
from app import selenium_utils as utils
from config import TIKTOK_OLD_COOKIES_FILENAME, DRIVER_PATH, LAUNCH_COOKIES

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def upload_video():
    driver = login_to_page()
    logger.info("Clicking on upload button")
    upload_button = utils.wait_for_element(driver, By.XPATH, '//div[@data-e2e="upload-icon"]')
    utils.move_mouse_and_click(driver, upload_button)

    logger.info("Uploading video")
    # TODO: actual video uploading, not a placeholder

    # Updating cookies
    logger.info("Saving current cookies")
    with open(TIKTOK_OLD_COOKIES_FILENAME, mode='w') as file:
        file.write(json.dumps(driver.get_cookies()))
    driver.quit()


def login_to_page() -> webdriver.Chrome:
    """
    Starts webdriver and opens home/start page with logged in account by using cookies
    (Before returning driver, waits for page to load)
    :return: Configured chromedriver
    """
    logger.info("Configuring driver for TikTok")
    driver = utils.get_configured_webdriver(DRIVER_PATH)
    # If old cookies exists using them instead
    if os.path.exists(TIKTOK_OLD_COOKIES_FILENAME):
        with open(TIKTOK_OLD_COOKIES_FILENAME, mode="r") as file:
            tiktok_cookies: List[dict] = json.loads(file.read())
    else:
        tiktok_cookies: List[dict] = LAUNCH_COOKIES["tiktok"]
    # Loading cookies to browser
    logger.info("Loading TikTok cookies")
    utils.set_cookies_for_browser(driver, tiktok_cookies)
    driver.get("https://tiktok.com")

    logger.info("Waiting for page to load")
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body")))
    except TimeoutException as e:
        logger.error("Can't load TikTok home page")

    return driver
