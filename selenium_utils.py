import math
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Info for move_mouse_and_click method
# TODO: maybe i should try to use middle screen cords (or [0, 0]) as initial cords.
# (since it's not that crucial + movements will be much more smoother)
previous_global_mouse_position = None


def wait_for_element(driver: webdriver.Chrome, by: By,
                     value: str, timeout=10) -> WebElement:
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located((by, value)))


def move_mouse_and_click(driver: webdriver.Chrome, destination_element) -> None:
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
        p0 = get_current_mouse_pos(driver)
    else:
        p0 = previous_global_mouse_position.copy()
    p3 = [int(destination_element.location['x']), int(destination_element.location['y'])]
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


def get_current_mouse_pos(driver: webdriver.Chrome) -> list:
    # Step 1. Create child element 1 by 1 pixel size
    current_element = driver.switch_to.active_element
    driver.execute_script("""
        var temp_img = document.createElement('img');
        temp_img.src = "data:,";
        temp_img.width = 1;
        temp_img.height = 1;
        temp_img.style.float = "center"
        // Source: https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentElement
        arguments[0].insertAdjacentElement("afterbegin", temp_img);
    """, current_element)
    # Step 2. Move mouse to this element
    actions = ActionChains(driver)
    position_source = current_element.find_element_by_xpath("(//img)[last()]")
    actions.move_to_element(position_source).perform()
    # Step 3. Get element position
    return [int(position_source.location['x']), int(position_source.location['y'])]


def set_cookies_for_browser(driver: webdriver.Chrome, cookies: List[dict]) -> None:
    """
    Adds cookies to driver BEFORE visiting any page by using chrome dev tools.
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
