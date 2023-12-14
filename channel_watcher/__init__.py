from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time
import sys
import os

from video_processor import Youbot
import utils.clear_folders as clear_folders

class ChannelWatcher():
  def __init__(self, channels, driver):
    self.channels = channels
    self.previous_video_titles = []
    """ op = webdriver.ChromeOptions()
    op.add_argument("--new-window")
    op.add_argument('--no-experiments')
    op.add_argument('user-data-dir=D:\\Users\\joaop\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default')
    op.add_argument('--disable-dev-shm-usage')
    op.add_argument('--disable-gpu')
    op.add_argument("--disable-infobars")
    op.add_argument("--log-level=3")
    op.add_argument("--disable-extensions")
    op.add_argument('--disable-popup-blocking') """
    #op.add_argument("headless")
    #op.add_argument("no-default-browser-check")
    #driver = webdriver.Chrome(options=op, desired_capabilities=d)
    #self.driver = uc.Chrome(options=op)
    self.driver = driver
    for channel in channels:
            self.driver.execute_script("window.open('https://www.youtube.com/{}/videos', '_blank'); window.focus();".format(channel))

  def check_for_new_videos(self):
        handles = self.driver.window_handles
        for i, handle in enumerate(handles):
            time.sleep(2)
            print(handle)
            print(i)
            self.driver.switch_to.window(handle)
            time.sleep(3)
            if(self.driver.title == "no-default-browser-check" or self.driver.title == "user-data-dir%3Dd"):
                self.driver.close()
                continue

            time.sleep(1)
            #self.driver.execute_script("window.focus('{}');".format(self.driver.title))
          
            video_elements = self.driver.find_elements(by=By.XPATH, value="/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]") #ytd-grid-video-renderer.style-scope.ytd-grid-renderer
            last_videos = [element.find_element(By.ID, "thumbnail") for element in video_elements] #video-title
            if last_videos != self.previous_video_titles:
                self.previous_video_titles = last_videos
                for last_video in last_videos:
                    last_video = last_video.get_attribute("href")
                    channel_name = self.driver.find_element(by=By.XPATH, value='//*[@id="channel-handle"]').text
                    return {
                        "uploaded": True,
                        "url": last_video,
                        "channel": channel_name
                    }
            else:
                continue
    
  def start_monitoring(self):
    while True:
        new_video = self.check_for_new_videos()
        if new_video is not None and new_video['uploaded']:
            #SHOULD GET THE !! METADATA !! OF THE VIDEO HERE!!!
            #ALSO WITH CHANNEL INFORMATION WE NEED TO KNOW THE LANGUAGE OF THE VIDEO, THE ACTION AND THE TO_LANGUAGE. THIS INFORMATIONS SHOULD COME FROM OUR DATABASE
            video = Youbot(self.driver, new_video['url'], 'Portuguese', 'translate', 'es')
            video.process_video()
            clear_folders.clear_folders()
            print("!!! IMPORTANT !!! CHECANDO A LISTA DE VIDEOS PASSADOS: ", self.previous_video_titles)
            continue
            # Add your desired actions here

        time.sleep(60)