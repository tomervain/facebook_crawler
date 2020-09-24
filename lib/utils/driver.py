from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options


def chromedriver(profile=1, headless=True, images=False, sandbox=True) -> WebDriver:
    """Creates a new Chromedriver session for Selenium

    Args:
        profile (int, optional): Chrome's profile to be used. Defaults to 1.
        headless (bool, optional): Running the driver in headless mode. Defaults to True.
        images (bool, optional): Enables rendreing of images. Defaults to False.
        sandbox (bool, optional): Running in sandbox mode (development). Defaults to True.

    Returns:
        WebDriver: Selenium webdriver object
    """
    driver_path = '/home/tomer/Temp/chromedriver'  # TODO: replace with enviroment variable
    # TODO: replace with enviroment variable
    chrome_path = Path('/home/tomer/.config/google-chrome/Default')
    profile_path = chrome_path / f'Profile {profile}'
    image_opt = 1 if images else 2
    driver_prefs = {
        "profile.managed_default_content_settings.images": image_opt,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 1,
        "profile.managed_default_content_settings.cookies": 1,
        "profile.managed_default_content_settings.javascript": 1,
        "profile.managed_default_content_settings.plugins": 1,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2
    }

    options = Options()
    options.add_argument(f'user-data-dir={profile_path}')
    if sandbox:
        options.add_argument("--no-sandbox")
    if headless:
        options.add_argument("--headless")

    # add driver's preferences and disable verbose logging
    options.add_experimental_option("prefs", driver_prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    return webdriver.Chrome(driver_path, options=options)


def facebook_login(driver: WebDriver, email: str, password: str):
    """Login to Facebook using account's email and password

    Args:
        driver (WebDriver): The webdriver used for login process
        email (str): Facebook account's email
        password (str): Facebook account's password
    """
    driver.get('http://facebook.com')
    if 'log in' in driver.title.lower():
        driver.find_element_by_name('email').send_keys(email)
        driver.find_element_by_name('pass').send_keys(password)
        driver.find_element_by_name('login').click()
        print(f'logged in as {email}')
    else:
        print('no login was issued')
