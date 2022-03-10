import os
import json

from app.logger_module import logger
from app import selenium_utils as utils

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def upload_video(path_to_cookies: str, chromedriver_path: str, path_to_video: str):
    logger.info(f"Starting upload for video: {path_to_video}")
    driver = login_to_page(chromedriver_path, path_to_cookies)
    logger.info("Clicking on upload button")
    upload_button = utils.wait_for_element(driver, By.XPATH, '//div[@data-e2e="upload-icon"]')
    utils.move_mouse_and_click(driver, upload_button)

    logger.info("Uploading video")
    # TODO: actual video uploading, not a placeholder
    # After video was posted we can delete it
    os.remove(path_to_video)

    # Updating cookies
    logger.info("Saving TikTok cookies")
    with open(path_to_cookies, mode='w') as file:
        file.write(json.dumps(driver.get_cookies()))
    driver.quit()


def login_to_page(chromedriver_path: str, path_to_cookies: str) -> webdriver.Chrome:
    """
    Starts webdriver and opens home/start page with logged in account by using cookies
    (Before returning driver, waits for page to load)
    :return: Configured chromedriver
    """
    logger.info("Configuring driver for TikTok")
    driver = utils.get_configured_webdriver(chromedriver_path)
    # If old cookies exists using them instead
    if os.path.exists(path_to_cookies):
        with open(path_to_cookies, mode="r") as file:
            tiktok_cookies: List[dict] = json.loads(file.read())
    else:
        logger.error("Can't find .json file with TikTok cookies for selenium")
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
