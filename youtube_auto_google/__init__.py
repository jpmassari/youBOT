import time
import random
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from utils.safer_click import safer_click

class YoutubeGoogle():

    def __init__(self, driver, login, password):
        self.driver = driver
        self.login = login,
        self.password = password
        
    def virtual_human(self, key, element):
        for j in key:
            for letter in j:
                time.sleep(random.uniform(0.04, 0.08))
                element.send_keys(letter)
                time.sleep(float("{:.2f}".format(random.uniform(0.02, 0.15))))

    def youtube_google(self):
        try:
            return self.__google()
        except Exception as e:
            print(e)
            raise

    def __google(self):
        try:
            WebDriverWait(self.driver, 1).until(
                EC.alert_is_present()
            )
            alert = self.driver.switch_to.alert
            alert.dismiss()  # or alert.accept() depending on your use case
        except Exception as e:
            print(f"Error handling alert: {e}")

        self.driver.get("https://accounts.google.com/SignOutOptions")
        account_list_elem = (By.XPATH, '//*[@id="account-list"]')
        account_list = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(account_list_elem)
        )
        for account in account_list:
            print("GOOGLE LOGIN -> ACCOUNT ID: ", account.id)
            if(self.login == "account-"+account.id):
                account.click_safe()
                WebDriverWait(self.driver, 15).until(
                    EC.url_contains('https://myaccount.google.com/')
                )
                break
        #TODO: RAISE APPLICATION IN CASE WE DON'T FIND ANY GOOGLE ACCOUNT WITH THE CORRECT NAME