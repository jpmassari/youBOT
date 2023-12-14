
from typing import DefaultDict, Optional

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from collections import defaultdict
import json
import time
from .Constant import *
from pathlib import Path
import logging
import platform
import os
import random
import unicodedata

logging.basicConfig()

class YouTubeUploader:
    """A class for uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc"""
          
    def __init__(self, driver: uc.Chrome, video_path, metadata_json: str, thumbnail_path: Optional[str] = None) -> None:
        """ op = webdriver.ChromeOptions()
        op.add_argument('--no-experiments')
        op.add_argument('user-data-dir=D:\\Users\\joaop\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
        op.add_argument('--disable-dev-shm-usage')
        op.add_argument('--disable-gpu')
        op.add_argument("--disable-infobars")
        op.add_argument("--log-level=3")
        op.add_argument("--disable-extensions") """
        #op.add_argument("headless")
        #op.add_argument("no-default-driver-check")
        #op.add_argument("no-first-run")
        #op.add_argument("no-sandbox")
        #driver = webdriver.Chrome(options=op, desired_capabilities=d)
        #self.driver = uc.Chrome(options=op)
        self.driver = driver
        self.thumbnail_path = thumbnail_path
        self.metadata_dict = metadata_json
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.video_path = video_path

    def upload(self):
        try:
            #self.__login()
            return self.__upload()
        except Exception as e:
            print(e)
            self.__quit()
            raise

    def virtual_human(self, key, element):
        for j in key:
            for letter in j:
                time.sleep(random.uniform(0.04, 0.08))
                element.send_keys(letter)
                time.sleep(float("{:.2f}".format(random.uniform(0.02, 0.15))))

    def __login(self):
        self.driver.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)
        #self.load_login_cookies()

        if self.driver.has_cookies_for_current_website():
            self.driver.load_cookies()
            time.sleep(Constant.USER_WAITING_TIME)
            self.driver.refresh()
        else:
            self.logger.info('Please sign in and then press enter')
            #input()
            #self.load_login_cookies()
            time.sleep(Constant.USER_WAITING_TIME)
            self.driver.get(Constant.YOUTUBE_URL)
            time.sleep(Constant.USER_WAITING_TIME)
            #self.driver.save_cookies()

    def __write_in_field(self, field, string, select_all=False, simulate_human=True):
        field.click()
        time.sleep(Constant.USER_WAITING_TIME)
        if select_all:
            field.send_keys(Keys.CONTROL + 'a')
            field.send_keys(Keys.DELETE)
            time.sleep(Constant.USER_WAITING_TIME)
        if(simulate_human):
            self.virtual_human(string, field)
        else:
            field.send_keys(string)

    def __upload(self):
        #self.driver.get(Constant.YOUTUBE_URL)
        #time.sleep(Constant.USER_WAITING_TIME)
        #self.driver.get(Constant.YOUTUBE_UPLOAD_URL)
        self.driver.execute_script("window.open('https://www.youtube.com/upload', '_blank');")
        time.sleep(5)
        handle = self.driver.current_window_handle
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])
        time.sleep(1)
        print("HANDLE: ", handle)
        print("HANDLES: ", handles)
        absolute_video_path = str(Path.cwd() / self.video_path)
        print("ABSOLUTE_VIDEO_PATH: ", absolute_video_path)
        self.driver.find_element(by=By.XPATH, value=Constant.INPUT_FILE_VIDEO).send_keys(
            absolute_video_path)
        self.logger.debug('Attached video {}'.format(self.video_path))
        
        time.sleep(15) #15
        if self.thumbnail_path is not None:
            absolute_thumbnail_path = str(Path('D:/workspaces/youbot/upload') / self.thumbnail_path)
            self.driver.find_element(by=By.XPATH, value=Constant.INPUT_FILE_THUMBNAIL).send_keys(
                absolute_thumbnail_path)
            change_display = "document.getElementById('file-loader').style = 'display: block! important'"
            self.driver.execute_script(change_display)
            self.logger.debug(
                'Attached thumbnail {}'.format(self.thumbnail_path))
        time.sleep(1) #should be more when working with thumbnail
        
        title_field = self.driver.find_element(by=By.ID, value=Constant.TEXTBOX)
        video_title = self.remove_non_bmp_characters(self.metadata_dict[Constant.VIDEO_TITLE])
        self.__write_in_field(
            title_field, video_title, select_all=True, simulate_human=False)
        self.logger.debug('The video title was set to \"{}\"'.format(
            self.metadata_dict[Constant.VIDEO_TITLE]))

        video_description = self.metadata_dict[Constant.VIDEO_DESCRIPTION]
        video_description = self.remove_non_bmp_characters(video_description)
        print("video description: ", video_description)
        video_description = video_description.replace("\n", Keys.ENTER)
        if video_description:
            #//ytcp-mention-textbox[@label='Description']//div[@id='textbox']
            description_field = self.driver.find_element(by=By.XPATH, value='/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-video-description/div/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div')
            time.sleep(random.uniform(1, 1.6))
            self.__write_in_field(description_field, video_description, select_all=True, simulate_human=False)
            self.logger.debug('Description filled.')

        time.sleep(random.uniform(0.5, 1.6))
        kids_section = self.driver.find_element(by=By.NAME, value= Constant.NOT_MADE_FOR_KIDS_LABEL)
        self.driver.execute_script("arguments[0].scrollIntoView();", kids_section)
        time.sleep(random.uniform(0.5, 1.6))
        kids_section.click()
        #self.driver.find_element_by_id(Constant.RADIO_LABEL, kids_section).click()
        self.logger.debug('Selected \"{}\"'.format(Constant.NOT_MADE_FOR_KIDS_LABEL))

        # Advanced options
        time.sleep(random.uniform(0.5, 1.6))
        self.driver.find_element(by=By.XPATH, value=Constant.MORE_BUTTON).click()
        self.logger.debug('Clicked MORE OPTIONS')

        #tags_container = self.driver.find_element_by_xpath(Constant.TAGS_INPUT_CONTAINER)
        #tags_field = self.driver.find_element_by_id(Constant.TAGS_INPUT, element=tags_container)
        #self.__write_in_field(tags_field, ','.join(self.metadata_dict[Constant.VIDEO_TAGS]))
        #self.logger.debug('The tags were set to \"{}\"'.format(self.metadata_dict[Constant.VIDEO_TAGS]))
        time.sleep(random.uniform(0.5, 1.6))
        self.driver.find_element(by=By.ID, value=Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} one'.format(Constant.NEXT_BUTTON))

        # Thanks to romka777
        time.sleep(random.uniform(0.5, 1.6))
        self.driver.find_element(by=By.ID, value=Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} two'.format(Constant.NEXT_BUTTON))

        time.sleep(random.uniform(0.5, 1.6))
        self.driver.find_element(by=By.ID, value= Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} three'.format(Constant.NEXT_BUTTON))
        #public_main_button = self.driver.find_element_by_name( Constant.PUBLIC_BUTTON)
        
        time.sleep(random.uniform(0.5, 1.6))
        self.driver.find_element(by=By.XPATH, value="//tp-yt-paper-radio-button[@name='PUBLIC']//div[@id='radioLabel']").click()
        self.logger.debug('Made the video {}'.format(Constant.PUBLIC_BUTTON))

        video_id = self.__get_video_id()

        status_container = self.driver.find_element(by=By.XPATH, value=Constant.STATUS_CONTAINER)
        while True:
            in_process = status_container.text.find(Constant.UPLOADED) != -1
            if in_process:
                print('Waiting uploading done....')
                time.sleep(Constant.USER_WAITING_TIME)
            else:
                break

        done_button = self.driver.find_element(by=By.ID, value=Constant.DONE_BUTTON)

        # Catch such error as
        # "File is a duplicate of a video you have already uploaded"
        if done_button.get_attribute('aria-disabled') == 'true':
            error_message = self.driver.find_element(by=By.XPATH, value=Constant.ERROR_CONTAINER).text
            self.logger.error(error_message)
            return False, None
        
        time.sleep(random.uniform(1, 1.6))
        done_button.click()
        self.logger.debug(
            "Published the video with video_id = {}".format(video_id))
        time.sleep(Constant.USER_WAITING_TIME)
        
        #self.save_cookies()
        
        time.sleep(5)
        
        #self.driver.get(Constant.YOUTUBE_URL)
        self.__quit()
        return True, video_id

    def __get_video_id(self) -> Optional[str]:
        video_id = None
        try:
            video_url_container = self.driver.find_element(by=By.XPATH, value=Constant.VIDEO_URL_CONTAINER)
            video_url_element = self.driver.find_element(by=By.XPATH, value=Constant.VIDEO_URL_ELEMENT)
            video_id = video_url_element.get_attribute(
                Constant.HREF).split('/')[-1]
        except:
            self.logger.warning(Constant.VIDEO_NOT_FOUND_ERROR)
            pass
        return video_id
    def remove_non_bmp_characters(self, text):
        #return ''.join(char for char in text if unicodedata.category(char) != 'So')
        return ''.join(char for char in text if ord(char) <= 0xFFFF)

    def __quit(self):
        self.driver.close()