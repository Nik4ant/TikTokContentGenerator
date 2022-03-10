import math
from typing import List, Any

from app.logger_module import logger

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium_stealth


# If None default value will be used
# (Used and updated by move_mouse_and_click function)
previous_global_mouse_position = None


def wait_for_element(driver: webdriver.Chrome, by: Any,
                     value: str, timeout=10) -> WebElement:
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.visibility_of_element_located((by, value)))
    except TimeoutException as e:
        logger.error(f"{driver.current_url} Can't located element by: \"{by}\" with value: {value}")


def move_mouse_and_click(driver: webdriver.Chrome, destination_element: WebElement) -> None:
    def linear_interpolation(point_0, point_1, t) -> list:
        """
        Calculate linear interpolation for given params
        :param point_0: Start point
        :param point_1: End point
        :param t: Coefficient for new point between p0 and p1 (0 is p0 and p1 is 1)
        :return: New point between p0 and p1
        """
        return [(1 - t) * point_0[0] + t * point_1[0], (1 - t) * point_0[1] + t * point_1[1]]
    global previous_global_mouse_position
    # To click on something like human we need to:
    # Step 1. Calculate points for mouse to follow using Cubic Bezier Curve
    # Step 2. Move mouse towards calculating points and then click on element
    if previous_global_mouse_position is None:
        # FIXME: middle screen position doesn't work with it.
        #  Because it's most likely that P1 and P2 are out of bounds
        # TODO: New way to calculate P1 and P2 OR new way to calculate curve
        p0 = [0, 0]
    else:
        p0 = previous_global_mouse_position.copy()
    # Destination element middle point
    p3 = [int(destination_element.location['x']) + destination_element.size["width"] * 0.5,
          int(destination_element.location['y']) + destination_element.size["height"] * 0.5]
    a = linear_interpolation(p0, p3, 0.5)
    p1_y = math.sqrt((p0[0] - a[0]) ** 2 + (p0[1] - a[1]) ** 2)
    p1 = [linear_interpolation(p0, a, 0.5)[0], p1_y]
    # Y coordinate is the same for p1 and p2
    p2 = [linear_interpolation(a, p3, 0.5)[0], p1_y]
    """
          * (P1) -- -- # -- -- (P2) * 
         /             |             \
        /              |              \
       /               |               \
      /                |                \
    * (P0) -- -- -- -- # -- -- -- -- (P3) * 
    Note: p0 and p3 can have different 'y' coordinate (this is just example)
    
    To calculate Cubic Bezier Curve path we need to know 
    points P1 and P2. But in this case there is no such points so
    i calculate them relative to P0 and P3 like this:
    
    1) A = linear_interpolation(P0, P3, 0.5)
    (So 'A' is a middle point between P0 and P3)
    2) Now we can define P1 as follow:
    P1.x = linear_interpolation(P0, A, 0.5)
    P1.y = sqrt((P0.x - A.x) ** 2 + (P0.y - A.y) ** 2)
    (P1.y equal to distance between P0 and A)
    3) Also in current scenario point must be offset a little bit to 
    simulate human like movements
    
    The similar process goes to calculate P2
    
    Now with this points we can easily calculate Cubic Bezier Curve. 
    Very good explanation video for that: https://youtu.be/aVwxzDHniEw?t=116
    """
    driver_actions = ActionChains(driver)
    current_mouse_position = p0.copy()
    t = 0.00
    t_changer = 0.1
    while t <= 1:
        # p_t is point on curve for current t
        p01 = linear_interpolation(p0, p1, t)
        p12 = linear_interpolation(p1, p2, t)
        p23 = linear_interpolation(p2, p3, t)
        d = linear_interpolation(p01, p12, t)
        e = linear_interpolation(p12, p23, t)
        p_t = linear_interpolation(d, e, t)
        driver_actions.move_by_offset(
            p_t[0] - current_mouse_position[0],
            p_t[1] - current_mouse_position[1])

        current_mouse_position[0] = p_t[0]
        current_mouse_position[1] = p_t[1]
        t += t_changer

    previous_global_mouse_position = current_mouse_position.copy()
    driver_actions.click()
    driver_actions.perform()


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


def set_cookies_for_browser(driver: webdriver.Chrome, cookies: List[dict]) -> None:
    """
    Adds cookies to driver by using chrome dev tools.
    Source: https://stackoverflow.com/a/63220249/13940541
    :param driver: chromedriver
    :param cookies: List with cookies
    """
    # Enables network tracking so we may use Network.setCookie method
    driver.execute_cdp_cmd('Network.enable', {})
    for cookie in cookies:
        # Fix issue Chrome exports 'expiry' key but expects 'expire' on import
        if 'expiry' in cookie:
            cookie['expires'] = cookie['expiry']
            del cookie['expiry']
        # Set the actual cookie
        driver.execute_cdp_cmd('Network.setCookie', cookie)

    # Disable network tracking
    driver.execute_cdp_cmd('Network.disable', {})
