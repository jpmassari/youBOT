from selenium import webdriver
import undetected_chromedriver as uc

class WebDriver():
	def __init__(self, headless=True, profile='Profile 10'):
		op = uc.ChromeOptions()
		op.add_argument("--new-window")
		op.add_argument('--no-experiments')
		#op.add_argument('user-data-dir=D:\\Users\\joaop\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default')
		#op.add_argument(f'--user-data-dir=D:\\Users\\joaop\\AppData\\Local\\Google\\Chrome\\User Data\\{profile}')
		op.user_data_dir = f'D:\\workspaces\\youBOT\\google profiles\\{profile}'
		op.add_argument('--disable-dev-shm-usage')
		op.add_argument('--disable-gpu')
		op.add_argument("--disable-infobars")
		op.add_argument("--log-level=3")
		op.add_argument("--disable-extensions")
		op.add_argument("--disable-popup-blocking")
		#op.add_argument("headless")
		#op.add_argument("no-default-browser-check")
		#driver = webdriver.Chrome(options=op, desired_capabilities=d)
		self.webdriver = uc.Chrome(headless=headless,options=op)
		#self.webdriver._web_element_cls = uc.webelement
	def driver(self):
		return self.webdriver