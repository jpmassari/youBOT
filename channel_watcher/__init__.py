from web_driver import WebDriver
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time
import sys
import subprocess
import os
from enum import Enum

import utils.clear_folders as clear_folders
from video_processor import Youbot
from db.database_operations import get_channel, get_my_channels, get_video_by_url, videos_uploaded_current_day

class ChannelWatcher():
    def __init__(self, channels):
        self.channels = channels
        self.previous_video_titles = []

    def check_shorts_tab(self, driver):
        tabs_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="tabsContent"]/yt-tab-group-shape/div[1]'))
        )
        #tabs = driver.find_element(By.XPATH, '//*[@id="tabsContent"]/yt-tab-group-shape/div[1]')
        tabs = tabs_container.find_elements(By.TAG_NAME, 'yt-tab-shape')
        for tab in tabs:
            tab = tab.find_element(By.XPATH, './/div[1]')
            if(tab.text == 'Shorts'):
                print("Encontrou tab shorts")
                return True
        print("!!Não encontrou tab shorts!!")
        return False

    def check_for_new_videos(self, channel, driver, video_list=[], content_type='videos'):
        try:
            WebDriverWait(driver, 1).until(
                EC.alert_is_present()
            )
            alert = driver.switch_to.alert
            alert.dismiss()  # or alert.accept() depending on your use case
        except Exception as e:
            print(f"Error handling alert: {e}")
            pass
        driver.get(f'https://www.youtube.com/{channel}/{content_type}')
        if(content_type == 'shorts'):
            shorts_tab = self.check_shorts_tab(driver)
            if(shorts_tab == False):
                return {
                    "url": None
                }

        driver._web_element_cls = uc.UCWebElement
        video_counter = 0
        video_scavanger = True
        while(video_scavanger):
            video_counter += 1
            video_elements_row = WebDriverWait(driver, 50).until(
                    EC.presence_of_all_elements_located((By.XPATH, f'//*[@id="contents"]/ytd-rich-grid-row[{video_counter}]')))   
            print(f"video elements length: {len(video_elements_row)}")
            #last_videos = [element.find_element(By.ID, "thumbnail").find_element(By.TAG_NAME, "a") for element in video_elements]
            for element_row in video_elements_row:
                videos = element_row.find_elements(By.TAG_NAME, "ytd-rich-item-renderer")
                for video in videos:
                    last_video = video.find_element(By.ID, "thumbnail")
                    if(content_type == 'videos'): 
                        last_video = last_video.find_element(By.TAG_NAME, "a")
                    print("last_video: ", last_video)
                    last_video_url = last_video.get_attribute("href")
                    print("last_video_url: ", last_video_url)
                    if(last_video_url in video_list): continue
                    channel_name = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="channel-handle"]'))
                    )
                    channel_name = channel_name.text
                    video_scavanger = False
                    break
            #channel_name = driver.find_element(by=By.XPATH, value='//*[@id="channel-handle"]').text
        return {
            "uploaded": True,
            "url": last_video_url,
            "channel": channel_name,
        }
        #if last_videos != self.previous_video_titles:
            #self.previous_video_titles = last_videos
    
    def start_monitoring(self):
        content_types = ['videos', 'shorts']
        mon_shorts = False
        for content_type in content_types:
            if(content_type == 'shorts'):
                mon_shorts = True
            for channel, my_channels in self.channels:
                last_language = ''
                try:
                    """ 
                        webdriver = WebDriver()
                        driver = webdriver.driver()
                        new_video = self.check_for_new_videos(channel, driver)
                    """
                    #TODO: a way to cache information from channels
                    language, description, shorts = get_channel(channel)
                    if(mon_shorts == True and shorts == 0):
                        #channels that don't have or we don't want to download shorts from
                        continue
                    elif(mon_shorts == False and shorts == 2):
                        #channels that we just want shorts
                        continue
                    clear_folders.clear_folders()
                    print("!!!!OUT OF MY CHANNELS!!!!")
                    for my_channel in my_channels:
                        try:
                            webdriver = WebDriver()
                            driver = webdriver.driver()
                            video_list = []
                            new_video = self.check_for_new_videos(channel, driver, video_list, content_type)
                            transcribe = True
                            if(new_video['url'] is None):
                                print("NO VIDEO WAS FOUND")
                                driver.quit()
                                break
                            
                            my_channel_id, to_language, action, translate_tags, google_email, google_password, google_country, google_profile = get_my_channels(my_channel)
                            was_uploaded = get_video_by_url(new_video['url'], my_channel_id)
                            while(was_uploaded):
                                video_list.append(new_video['url'])
                                new_video = self.check_for_new_videos(channel, driver, video_list, content_type)
                                print(f"This video {new_video['url']} was already uploaded in this channel {my_channel_id}")
                                print("GETTING AN OLDER VIDEO")
                                was_uploaded = get_video_by_url(new_video['url'], my_channel_id)
                            driver.quit()
                
                            schedule = videos_uploaded_current_day(my_channel_id)
                            if(last_language == to_language):
                                last_language = to_language
                                transcribe = False
                            last_language = to_language
                            if(mon_shorts == True):
                                schedule = 0
                            video = Youbot(my_channel, new_video['url'], language, description, my_channel_id, to_language, action, translate_tags, google_email, google_password, google_country, google_profile, schedule, transcribe, mon_shorts) #Portuguese, translate, en(to_language)
                            video.process_video()
                        except Exception as e:
                            print(f'An error ocurred while monitoring this channel: {e}')
                            driver.quit()
                            continue
                    # Add your desired actions here
                except Exception as e:
                    print(f'an error before looping in mychannels {e}')
                    continue
                    #raise SystemExit(1)
            try:
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], check=True)
                print("Google Chrome process killed successfully.")
            except subprocess.CalledProcessError as e:
                print(e)
        print("Terminamos de loopar entre todos os canais, vamos de novo com shorts!!")
        sys.exit()