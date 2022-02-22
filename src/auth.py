import os
import pickle
import time

from loguru import logger
from selenium.webdriver.common.keys import Keys

from setup.config import Config
from src.cookies import ParserCookies
from src.webdrivermanager import DriverManager


class Auth:
    def __init__(self, driver: DriverManager, conf: Config, cookies: ParserCookies, log: logger):
        self.driver = driver
        self.conf = conf
        self.cookies = cookies
        self.log = log

    def login(self):
        self.driver.delete_all_cookies()
        self.driver.change_location(self.conf.Navigate.auth_page, self.conf.Wait.s_7)
        self.log.info("Start auth")

        self.driver.make_screenshot("auth_page_login_input")
        if not self.driver.send_keys(self.conf.Navigate.auth_form_login_input, self.conf.Yandex.email):
            self.log.warning('Login input NOT exists')
            return False
        self.log.info('Login entered')
        time.sleep(self.conf.Wait.s_3)

        if not self.driver.send_keys(self.conf.Navigate.auth_form_login_input, Keys.ENTER):
            self.log.warning('Can`t press enter after login input')
            self.driver.make_screenshot('after_login_press_enter')
            return False
        self.log.info('Enter pressed')
        time.sleep(self.conf.Wait.s_5)
        self.driver.make_screenshot("auth_page_password_input")
        if not self.driver.send_keys(self.conf.Navigate.auth_form_password_input, self.conf.Yandex.password):
            self.log.warning('Password input NOT exists')
            return False
        self.log.info('Password entered')
        time.sleep(self.conf.Wait.s_3)

        if not self.driver.send_keys(self.conf.Navigate.auth_form_password_input, Keys.ENTER):
            self.log.warning('Can`t press enter after password input')
            self.driver.make_screenshot('after_password_press_enter')
            return False
        self.log.info('Enter pressed')
        time.sleep(self.conf.Wait.s_7)

        self.driver.make_screenshot('after_auth_state')

        self.log.info('Checking sms confirmation button')
        if self.driver.clik(self.conf.Navigate.phone_confirm_button):
            self.log.info(f'Waiting sms code for {self.conf.Wait.s_45} sec')
            time.sleep(self.conf.Wait.s_45)
            self.log.info('Try reading sms code from file')
            if not os.path.exists(self.conf.confirm_code_file_path):
                self.log.info('Error file with sms not exists')
            self.log.info('File with sms exists')
            code = open(self.conf.confirm_code_file_path, 'r').read()
            if not len(code):
                self.log.warning(f"Error sms confirmation code is empty in '{self.conf.confirm_code_file_path}'")
                return False
            self.log.info(f'Start input code: {code}')
            if not self.driver.send_keys(self.conf.Navigate.sms_confirm_input, code):
                self.log.warning('Error sms confirmation input not exists')
                return False
            self.log.info('sms code inputted')

            time.sleep(self.conf.Wait.s_7)
            if not self.driver.send_keys(self.conf.Navigate.sms_confirm_input, Keys.ENTER):
                self.log.warning('Can`t press enter after sms code input')
                return False
            self.log.info('Enter pressed')
            time.sleep(self.conf.Wait.s_7)
            self.driver.make_screenshot("after_sms_state")
        self.driver.change_location(self.conf.Navigate.working_page, self.conf.Wait.s_7)
        self.driver.make_screenshot("check_successful_auth")
        self.log.info('Checking successful auth')
        if not self.driver.get_element(self.conf.Navigate.authorized_flag):
            self.log.warning('Auth failed')
            time.sleep(self.conf.Wait.s_7)
            return False
        self.log.info('Auth is successful')
        time.sleep(self.conf.Wait.s_7)
        pickle.dump(self.driver.get_cookies(), open(self.conf.cookies_path, 'wb'))
        time.sleep(self.conf.Wait.s_5)
        return True

    def restore_from_cookies(self):
        self.log.info('Try to load cookies')
        self.driver.change_location(self.conf.Navigate.working_page, self.conf.Wait.s_7)
        self.driver.make_screenshot("before_cookies_restore_state")
        try:
            if not self.cookies.restore():
                self.log.warning('Cookies file is empty')
                return False
            self.log.info('Cookies are loaded')

            time.sleep(self.conf.Wait.s_3)
            self.driver.change_location(self.conf.Navigate.working_page, self.conf.Wait.s_7)
            self.driver.make_screenshot("after_cookies_restore_state")
            self.log.info('Checking successful auth')
            if not self.driver.get_element(self.conf.Navigate.authorized_flag):
                self.log.warning('Auth failed')
                self.driver.make_screenshot("error_auth_by_cookie")
                time.sleep(self.conf.Wait.s_3)
                return False
            self.log.info('Auth by cookies is successful')
            time.sleep(self.conf.Wait.s_5)
            self.log.info('Updating COOKIES')
            pickle.dump(self.driver.get_cookies(), open(self.conf.cookies_path, 'wb'))
            time.sleep(self.conf.Wait.s_5)
            return True
        except Exception as er:
            self.log.warning('Error on cookies loading')
            self.log.error(str(er))
            return False
