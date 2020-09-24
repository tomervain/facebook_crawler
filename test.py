from lib.utils.driver import chromedriver

try:
    driver = chromedriver(headless=False, images=True)
    input('halt...')
finally:
    driver.quit()