from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager

from backend.hostLogin import join_meeting
from backend.hostBottomMenu import ZoomBottomMenu

class ZoomBackend(ZoomBottomMenu):
	def __init__(self, headless):
		self.driver = self.init_driver(headless)
		super().__init__(self.driver)

	def init_driver(self, headless):
		options = Options()
		options.headless = headless
		# Extensions to solve ReCaptcha
		options.add_extension("./extension/Captcha.crx")
		options.add_extension("./extension/CORSon.crx")
		# List of options to avoid reCaptcha
		options.add_argument("start-maximized")
		options.add_argument('--profile-directory=profile')
		options.add_argument("--disable-blink-features")
		options.add_argument('--disable-gpu')
		options.add_argument('--no-sandbox')
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)
		options.add_argument("--disable-blink-features=AutomationControlled")
		options.add_argument("--use-fake-ui-for-media-stream")
		options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36')
		# Linux
		driver=Chrome("./chromedriver.exe",options=options)
		# Windows 
		# driver=Chrome(ChromeDriverManager().install(),options=options)
		return driver
	
	def start_driver(self,url, meeting_id, meeting_pwd):
		print("\nZoomPlusPlus Backend (Host)\n")
		if join_meeting(self.driver, url, meeting_id, meeting_pwd):
			super().get_participants_list()
			super().call_next_person("raise_hands")
			return self.driver
		else:
			print("Failed to start driver")
			return None

if __name__ == '__main__':
	backend = ZoomBackend(False)
	meeting_id = "" # Enter meeting id
	meeting_pwd = "" # Enter meeting pwd
	backend.start_driver(None,meeting_id,meeting_pwd)