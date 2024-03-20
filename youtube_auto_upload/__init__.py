
from typing import DefaultDict, Optional

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
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
from datetime import datetime

from youtube_auto_login import YoutubeLogin
from utils.clear_special_characters import remove_non_bmp_characters
from utils.safer_click import safer_click

logging.basicConfig()

class YouTubeUploader:          
    def __init__(self, driver: uc.Chrome, video_path, metadata_json: str, schedule, thumbnail_path: Optional[str] = None) -> None:
        self.driver = driver
        self.video_path = video_path
        self.metadata_dict = metadata_json
        self.thumbnail_path = thumbnail_path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.schedule = schedule

    def youtube_upload(self):
        try:
            return self.__upload()
        except Exception as e:
            print(e)
            self.driver.quit()
            raise

    def virtual_human(self, key, element):
        for letter in key:
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
        safer_click(field)
        time.sleep(Constant.USER_WAITING_TIME)
        if select_all:
            field.send_keys(Keys.CONTROL + 'a')
            time.sleep(random.uniform(0.5, 1.6))
            field.send_keys(Keys.DELETE)
            time.sleep(random.uniform(0.5, 0.8))
        if(simulate_human):
            self.virtual_human(string, field)
        else:
            field.send_keys(string)

    def __upload(self):
        #self.driver.get(Constant.YOUTUBE_URL)
        #time.sleep(Constant.USER_WAITING_TIME)
        try:
            WebDriverWait(self.driver, 3).until(
                EC.alert_is_present()
            )
            alert = self.driver.switch_to.alert
            alert.dismiss()  # or alert.accept() depending on your use case
        except Exception as e:
            print(f"Error handling alert: {e}")

        self.driver.get(Constant.YOUTUBE_UPLOAD_URL)
        try:
            WebDriverWait(self.driver, 20).until(
                EC.url_matches('https://www.youtube.com/channel/')
            )
        except TimeoutException:
            # Handle the TimeoutException here
            print("TimeoutException YOUTUBE_AUTO_UPLOAD: The URL in did not match within the specified timeout period.")
            self.driver.get(Constant.YOUTUBE_UPLOAD_URL)

        #self.driver.execute_script("window.open('https://www.youtube.com/upload', '_blank');")
        time.sleep(5)
        handle = self.driver.current_window_handle
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])
        time.sleep(1)
        absolute_video_path = str(Path.cwd() / self.video_path)
        print("ABSOLUTE_VIDEO_PATH: ", absolute_video_path)
        try:
            upload_video = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, Constant.INPUT_FILE_VIDEO))
            )
            upload_video.send_keys(absolute_video_path)
            self.logger.debug('Attached video {}'.format(self.video_path))
        except:
            upload_video = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, Constant.INPUT_FILE_VIDEO))
            )
            upload_video.send_keys(absolute_video_path)
        #self.driver.find_element(by=By.XPATH, value=Constant.INPUT_FILE_VIDEO).send_keys(absolute_video_path)

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
        
        #title_field = self.driver.find_element(by=By.ID, value=Constant.TEXTBOX)
        try:
            title_field = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.ID, Constant.TEXTBOX))
            )
        except:
            title_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, Constant.TEXTBOX))
            )
        time.sleep(random.uniform(0.5, 1.6))
        video_title = remove_non_bmp_characters(self.metadata_dict[Constant.VIDEO_TITLE])
        self.__write_in_field(
            title_field, video_title, select_all=True, simulate_human=False)
        self.logger.debug('The video title was set to \"{}\"'.format(
            self.metadata_dict[Constant.VIDEO_TITLE]))

        video_description = self.metadata_dict[Constant.VIDEO_DESCRIPTION]
        video_description = remove_non_bmp_characters(video_description)
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
        safer_click(kids_section)
        self.logger.debug('Selected \"{}\"'.format(Constant.NOT_MADE_FOR_KIDS_LABEL))

        # Advanced options
        time.sleep(random.uniform(0.5, 1.6))
        advanced_options = self.driver.find_element(by=By.XPATH, value=Constant.MORE_BUTTON)
        safer_click(advanced_options)
        self.logger.debug('Clicked MORE OPTIONS')

        #tags
        tag_field_locator = (By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-advanced/div[5]/ytcp-form-input-container/div[1]/div/ytcp-free-text-chip-bar/ytcp-chip-bar/div/input')
        tag_field = WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located(tag_field_locator)
        )
        for tag in self.metadata_dict[Constant.VIDEO_TAGS]:
            time.sleep(random.uniform(0.04, 0.20))
            tag_field.send_keys(tag)
            time.sleep(float("{:.2f}".format(random.uniform(0.06, 0.15))))
            time.sleep(random.uniform(0.04, 0.012))
            tag_field.send_keys(',')
            time.sleep(float("{:.2f}".format(random.uniform(0.06, 0.15))))
            self.logger.debug('inserted tag \"{}\"'.format(tag))

        try:
            next_button_1 = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.ID, Constant.NEXT_BUTTON))
            )
            time.sleep(random.uniform(0.5, 1.6))
            safer_click(next_button_1)
            self.logger.debug('Clicked {} one'.format(Constant.NEXT_BUTTON))
        except:
            next_button_1 = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, Constant.NEXT_BUTTON))
            )
            safer_click(next_button_1)
        #self.driver.find_element(by=By.ID, value=Constant.NEXT_BUTTON).click()

        # Thanks to romka777
        try:
            next_button_2 = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.ID, Constant.NEXT_BUTTON))
            )
            time.sleep(random.uniform(0.5, 1.6))
            safer_click(next_button_2)
            self.logger.debug('Clicked {} two'.format(Constant.NEXT_BUTTON))
        except:
            next_button_2 = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, Constant.NEXT_BUTTON))
            )
            safer_click(next_button_2)

        """ time.sleep(random.uniform(0.5, 1.6))
        self.driver.find_element(by=By.ID, value=Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} two'.format(Constant.NEXT_BUTTON)) """

        try:
            next_button_3 = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.ID, Constant.NEXT_BUTTON))
            )
            time.sleep(random.uniform(0.5, 1.6))
            safer_click(next_button_3)
            self.logger.debug('Clicked {} one'.format(Constant.NEXT_BUTTON))
        except:
            next_button_3 = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, Constant.NEXT_BUTTON))
            )
            safer_click(next_button_3)
        """ time.sleep(random.uniform(0.5, 1.6))
        self.driver.find_element(by=By.ID, value= Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} three'.format(Constant.NEXT_BUTTON)) """
        #public_main_button = self.driver.find_element_by_name( Constant.PUBLIC_BUTTON)
        
        try:
            set_public = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']//div[@id='radioLabel']"))
            )
            time.sleep(random.uniform(0.5, 1.6))
            safer_click(set_public)
            self.logger.debug('Made the video {}'.format(Constant.PUBLIC_BUTTON))
        except TimeoutException:
            # Handle the TimeoutException here
            print("Element //tp-yt-paper-radio-button[@name='PUBLIC']//div[@id='radioLabel'] not Found. Trying one more time")
            set_public = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']//div[@id='radioLabel']"))
            )
            safer_click(set_public)

        print("schedule: ", self.schedule)
        if(self.schedule > 0):
            date = datetime.now()
            current_day = date.day
            print("current_day: ", current_day)
            current_hour = date.hour
            schedule_hour = current_hour + self.schedule
            formated_schedule_hour = str(schedule_hour) + ":00" 
            try:
                self.__set_schedule(current_day, formated_schedule_hour)

                self.logger.debug('Video upload successfully scheduled')
            except TimeoutException:
                # Handle the TimeoutException here
                print("Had a problem setting scheduling video upload. Trying one more time")
                self.__set_schedule(current_day, formated_schedule_hour)
        
        video_id, video_url = self.__get_video_id()
        print("video_id: ", video_id)
        try:
            status_container = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, Constant.STATUS_CONTAINER))
            )
        except:
            status_container = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, Constant.STATUS_CONTAINER))
            )
        #status_container = self.driver.find_element(by=By.XPATH, value=Constant.STATUS_CONTAINER)
        while True:
            in_process = status_container.text.find(Constant.UPLOADED) != -1
            if in_process:
                print('Waiting uploading done....')
                time.sleep(Constant.USER_WAITING_TIME)
            else:
                break
        try:
            done_button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="done-button"]'))
            )
        except:
            done_button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="done-button"]'))
            )
        #done_button = self.driver.find_element(by=By.ID, value=Constant.DONE_BUTTON)

        # Catch such error as
        # "File is a duplicate of a video you have already uploaded"
        """ if done_button.get_attribute('aria-disabled') == 'true':
            error_message = self.driver.find_element(by=By.XPATH, value=Constant.ERROR_CONTAINER).text
            self.logger.error(error_message)
            return False, None """
        
        time.sleep(random.uniform(1, 1.6))
        safer_click(done_button)
        self.logger.debug(
            "Published the video with video_id = {}".format(video_id))
        time.sleep(Constant.USER_WAITING_TIME)
        
        #self.save_cookies()
        
        #self.driver.get(Constant.YOUTUBE_URL)
        #self.driver.close()
        return video_id, video_url

    def __get_video_id(self) -> Optional[str]:
        video_id = None
        try:
            #video_url_container = self.driver.find_element(by=By.XPATH, value=Constant.VIDEO_URL_CONTAINER)
            video_url_element = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, Constant.VIDEO_URL_ELEMENT))
            )
            #video_url_element = self.driver.find_element(by=By.XPATH, value=Constant.VIDEO_URL_ELEMENT)
            video_id = video_url_element.get_attribute(
                Constant.HREF).split('/')[-1]
            return video_id, video_url_element.text
        except:
            self.logger.warning(Constant.VIDEO_NOT_FOUND_ERROR)
            video_url_element = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, Constant.VIDEO_URL_ELEMENT))
            )
            #video_url_element = self.driver.find_element(by=By.XPATH, value=Constant.VIDEO_URL_ELEMENT)
            video_id = video_url_element.get_attribute(
                Constant.HREF).split('/')[-1]
            return video_id, video_url_element.text


    def __set_schedule(self, current_day, formated_schedule_hour):
        schedule_button = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "second-container-expand-button"))
        )
        time.sleep(random.uniform(0.5, 1.6))
        safer_click(schedule_button)
        time.sleep(random.uniform(0.5, 1.6))
        schedule_calendar_button = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="datepicker-trigger"]/ytcp-dropdown-trigger/div/div[3]'))
        )
        time.sleep(random.uniform(0.5, 1.6))
        safer_click(schedule_calendar_button)
        time.sleep(random.uniform(0.5, 1.6))
        schedule_calendar = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="items"]/div[1]'))
        )
        schedule_calendar_weeks = schedule_calendar.find_elements(by=By.TAG_NAME, value='div')
        for div in schedule_calendar_weeks:
            div_class = div.get_attribute('class')
            if('calendar-month-label' in div_class):
                continue
            spans = div.find_elements(by=By.TAG_NAME, value='span')
            for span in spans:
                if not span.text: continue
                calendar_day = int(span.text)
                print("span value: ", span.text)
                if(calendar_day == current_day):
                    safer_click(span)
                    time.sleep(random.uniform(0.5, 1.6))
                    break
        time.sleep(random.uniform(0.5, 1.6))
        try:
            schedule_date = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="input-1"]/input'))
            )
            self.__write_in_field(schedule_date, formated_schedule_hour, True, True)
            time.sleep(random.uniform(0.5, 1.6))
        except:
            schedule_date = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="input-1"]/input'))
            )
            self.__write_in_field(schedule_date, formated_schedule_hour, True, True)
            time.sleep(random.uniform(0.5, 1.6))
        schedule_date.send_keys(Keys.ESCAPE)
