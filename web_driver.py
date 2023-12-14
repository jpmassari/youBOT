from selenium import webdriver
import undetected_chromedriver as uc

class WebDriver():
	def __init__(self):
		op = webdriver.ChromeOptions()
		op.add_argument("--new-window")
		op.add_argument('--no-experiments')
		op.add_argument('user-data-dir=D:\\Users\\joaop\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default')
		op.add_argument('--disable-dev-shm-usage')
		op.add_argument('--disable-gpu')
		op.add_argument("--disable-infobars")
		op.add_argument("--log-level=3")
		op.add_argument("--disable-extensions")
		op.add_argument('--disable-popup-blocking')
		#op.add_argument("headless")
		#op.add_argument("no-default-browser-check")
		#driver = webdriver.Chrome(options=op, desired_capabilities=d)
		self.webdriver = uc.Chrome(options=op)
	
	def driver(self):
		return self.webdriver