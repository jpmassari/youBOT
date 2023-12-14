import time
import random
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

class YoutubeLogin():

    def __init__(self, login, password):
        self.login = login,
        self.password = password
        
    def virtual_human(self, key, element):
        for j in key:
            for letter in j:
                time.sleep(random.uniform(0.04, 0.08))
                element.send_keys(letter)
                time.sleep(float("{:.2f}".format(random.uniform(0.02, 0.15))))

    def youtube_login(self):
        op = webdriver.ChromeOptions()
        op.add_argument('--no-experiments')
        op.add_argument('user-data-dir=D:\\Users\\joaop\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default')
        op.add_argument('--disable-dev-shm-usage')
        op.add_argument('--disable-gpu')
        op.add_argument("--disable-infobars")
        op.add_argument("--log-level=3")
        op.add_argument("--disable-extensions")
        #op.add_argument("headless")
        op.add_argument("no-default-browser-check")
        op.add_argument("no-first-run")
        op.add_argument("no-sandbox")
        #driver = webdriver.Chrome(options=op, desired_capabilities=d)
        driver = uc.Chrome(options=op)
        driver.implicitly_wait(6)
        driver.execute_script("document.body.style.zoom='80%'")
        driver.get('https://accounts.google.com/signin/v2/identifier?service=youtube&uilel=3&passive=true&continue=https'
                '%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dht'
                'tps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
        #driver.delete_all_cookies()
        # finding email field and putting our email on it
        """ driver.delete_all_cookies()
        cookie_files = os.listdir('./cookies')
        is_files = False
        for i, files in enumerate(cookie_files):
            if(files):
                file_path = os.path.join('./cookies', f'cookie{i}.json')
                driver.add_cookie(
                    json.load(open(
                        file_path,
                        'r'
                    )
                ))
                is_files = True
        if(is_files):
            return driver """
        email_field = driver.find_element(by=By.XPATH, value='//*[@id="identifierId"]')
        self.virtual_human(self.login, email_field)
        time.sleep(random.uniform(0.5, 1.1))
        email_field.send_keys(Keys.ENTER)
        #driver.find_element(by=By.ID, value="identifierNext").click()
        time.sleep(5)

        # finding pass field and putting our pass on it
        find_pass_field = (By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')
        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located(find_pass_field))
        pass_field = driver.find_element(*find_pass_field)
        WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable(find_pass_field))
        self.virtual_human(self.password, pass_field)
        pass_field.send_keys(Keys.ENTER)
        #driver.find_element(by=By.ID, value="passwordNext").click()
        time.sleep(5)
        print("password - done")
        WebDriverWait(driver, 200).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ytd-masthead button#avatar-btn")))

        cookie_files = os.listdir('./cookies')
        for files in cookie_files:
            if(files):
                print("shoudln't")
                return driver

        cookies = driver.get_cookies()
        for i, cookie in enumerate(cookies):
            print(cookie)
            file_path = os.path.join('./cookies', f'cookie{i}.json')
            with open(file_path, 'w') as json_file:
                json.dump(cookie, json_file)

        return driver