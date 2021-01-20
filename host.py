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
	
	def start(self):
		print("\nZoomPlusPlus Backend (Host)\n")
		join_meeting(self.driver)
		print("Done")

if __name__ == '__main__':
	backend = ZoomBackend(False)
	backend.start()