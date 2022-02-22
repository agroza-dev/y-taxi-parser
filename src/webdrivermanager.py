import time
from datetime import datetime
from typing import List

from loguru import logger
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

from setup.config import Config


class DriverManager:
    def __init__(self, config: Config, log: logger):
        self.conf = config
        self.log = log
        self.driver = None
        self.display = None

    def init(self):
        if not self.conf.debug_mode:
            self.display = Display(
                visible=self.conf.Display.visible,
                size=(self.conf.Display.width, self.conf.Display.height)
            )
            self.display.start()
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--start-maximized' if self.conf.debug_mode else '--headless')
        chrome_options.add_argument(f'window-size={self.conf.Display.width}x{self.conf.Display.height}')
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": self.conf.Driver.start_latitude,
            "longitude": self.conf.Driver.start_longitude,
            "accuracy": 100
        })

    def get_element(self, path: str, _by: str = By.XPATH) -> WebElement:
        try:
            result = self.driver.find_element(_by, path)
        except NoSuchElementException:
            self.log.warning(f'{path} - not found')
            result = None
        return result

    def get_element_text(self, path: str, _by=By.XPATH):
        result = False
        try:
            element = self.get_element(path)
            if element:
                result = element.text
        except Exception as e:
            self.log.error(f'Can`t get text for element: {path} . {str(e)}')
        finally:
            return result

    def change_location(self, url: str, sleap_time: int = 0):
        self.driver.get(url)
        if sleap_time > 0:
            time.sleep(sleap_time)

    def send_keys(self, path: str, keys: str, path_type: str = By.XPATH, pre_clear=False) -> bool:
        result = False
        try:
            self.log.debug(f'Try to send "{keys}" to {path}]')
            dom_element = self.get_element(path, path_type)
            if dom_element:
                if pre_clear:
                    dom_element.send_keys(Keys.CONTROL + 'a')
                    time.sleep(self.conf.Wait.s_1)
                dom_element.send_keys(keys)
                result = True
        except Exception as e:
            self.log.error(f'Element error: {str(e)} - {path}')
        finally:
            return result

    def clik(self, path: str, path_type: str = By.XPATH) -> bool:
        dom_element = self.get_element(path, path_type)
        if dom_element:
            dom_element.click()
            return True
        return False

    def make_screenshot(self, name: str) -> None:
        if self.conf.Screenshots.enabled:
            full_name = f'{self.conf.Screenshots.path}{datetime.now().strftime("%d-%m-%Y_%H_%M")}_{name}.png'
            self.driver.save_screenshot(full_name)

    def destroy(self) -> None:
        if self.driver:
            self.log.info('Driver destroyed!')
            self.driver.close()
            self.driver.quit()
        if self.display and self.display.is_alive():
            self.display.stop()

    def get_cookies(self) -> List[dict]:
        return self.driver.get_cookies()

    def delete_all_cookies(self) -> None:
        return self.driver.delete_all_cookies()

    def add_cookie(self, cookie) -> None:
        self.driver.add_cookie(cookie)
