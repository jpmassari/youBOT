from channel_watcher import ChannelWatcher
from video_processor import Youbot
from web_driver import WebDriver

def main():
    webdriver = WebDriver()
    driver = webdriver.driver()
    channels = ['@compantokrator']
    channelWatcher = ChannelWatcher(channels, driver)
    channelWatcher.start_monitoring()
    """ video = Youbot(driver, 'https://www.youtube.com/watch?v=zxjlkk7tl_A', 'German', 'translate', 'pt')
    video.process_video() """

if __name__ == "__main__":
    main()