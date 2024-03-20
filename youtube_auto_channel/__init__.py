import time
import random
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from utils.safer_click import safer_click

class YoutubeChannel():
    def __init__(self, driver, my_channel):
        self.driver = driver
        self.my_channel = my_channel

    def youtube_channel(self):
        try:
            self.__channel()
        except Exception as e:
            print(e)
            #self.driver.quit()
            self.__channel()

    def __channel(self):
        try:
            WebDriverWait(self.driver, 1).until(
                EC.alert_is_present()
            )
            alert = self.driver.switch_to.alert
            alert.dismiss()  # or alert.accept() depending on your use case
        except Exception as e:
            print(f"Error handling alert: {e}")
            
        self.driver.get('https://www.youtube.com/channel_switcher')
        try:
            WebDriverWait(self.driver, 20).until(
                EC.url_matches('https://www.youtube.com/account')
            )
        except TimeoutException:
            # Handle the TimeoutException here
            print("TimeoutException YOUTUBE_AUTO_CHANNEL: The URL in did not match within the specified timeout period.")
            self.driver.get('https://www.youtube.com/channel_switcher')
        # Define the XPath for the elements with id "contents"
        contents_elements_xpath = '//*[@id="contents"]'

        # Wait for at least three elements with the id "contents"
        contents_elements = WebDriverWait(self.driver, 50).until(
            EC.presence_of_all_elements_located((By.XPATH, contents_elements_xpath)))
        print("CONTENTS LEN: ", len(contents_elements))
        # Check if there are at least three elements
        if len(contents_elements) >= 3:
            print("START TO LOOP THROUGH CHANNEL")
            third_contents_element = contents_elements[2]
            WebDriverWait(self.driver, 50).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'ytd-account-item-renderer')))
            channels = third_contents_element.find_elements(By.TAG_NAME, 'ytd-account-item-renderer')
            for i, channel in enumerate(channels):
                channel_name = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="contents"]/ytd-account-item-renderer[{i+1}]/tp-yt-paper-icon-item/tp-yt-paper-item-body/yt-formatted-string[2]'))
                )
                #channel_name = channel.find_element(By.XPATH, f'//*[@id="contents"]/ytd-account-item-renderer[{i+1}]/tp-yt-paper-icon-item/tp-yt-paper-item-body/yt-formatted-string[2]')
                print("CHANNEL_NAME TEXT: ", channel_name.text)
                print("VERIFY MY CHANNEL: ", self.my_channel)
                if(channel_name.text == self.my_channel):
                    safer_click(channel)
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.url_matches('https://www.youtube.com/')
                        )
                    except TimeoutException:
                        # Handle the TimeoutException here
                        print("TimeoutException YOUTUBE_AUTO_CHANNEL: The URL did not match within the specified timeout period.")
                        safer_click(channel)
                        
                    break
            #TODO: RAISE APPLICATION IN CASE WE DON'T FIND ANY CHANNEL WITH THE CORRECT NAME
        
            """             upload_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="buttons"]/ytd-topbar-menu-button-renderer[1]'))
            )
            upload_button.click_safe() """
