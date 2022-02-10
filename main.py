import os
import json
from typing import List

import selenium_utils

from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium_stealth


# Loading config
with open("config.json", mode="r") as config_file:
    global_config: dict = json.loads(config_file.read())


def get_configured_webdriver(path_to_driver: str) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "disable-popup-blocking"])
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    options.add_argument("--mute-audio")
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options, executable_path=path_to_driver)

    selenium_stealth.stealth(driver,
                             languages=["en-US", "en"],
                             vendor="Google Inc.",
                             platform="Win32",
                             webgl_vendor="Intel Inc.",
                             renderer="Intel Iris OpenGL Engine",
                             fix_hairline=True,
                             )
    return driver


def main():
    driver = get_configured_webdriver(global_config["PATH_TO_DRIVER"])
    # If old cookies exists using them instead
    if os.path.exists(global_config["TIKTOK_OLD_COOKIES_FILENAME"]):
        with open(global_config["TIKTOK_OLD_COOKIES_FILENAME"], mode="r") as file:
            tiktok_cookies: List[dict] = json.loads(file.read())
    else:
        tiktok_cookies: List[dict] = global_config["launch_cookies"]["tiktok"]
    # Loading coolies to browser
    selenium_utils.set_cookies_for_browser(driver, tiktok_cookies)
    driver.get("https://tiktok.com")

    # Updating cookies
    with open(global_config["TIKTOK_OLD_COOKIES_FILENAME"], mode='w') as file:
        file.write(json.dumps(driver.get_cookies()))
    driver.quit()


if __name__ == '__main__':
    main()
