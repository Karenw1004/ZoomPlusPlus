from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager

from backend.hostLogin import join_meeting
from backend.hostBottomMenu import ZoomBottomMenu
from backend.hostVideo import ZoomVideo

class ZoomBackend(ZoomBottomMenu, ZoomVideo):
	def __init__(self, headless):
		self.driver = self.init_driver(headless)
		super().__init__(self.driver)
		self.raised_hands_list = []

	def init_driver(self, headless):
		options = Options()
		options.headless = headless
		# if not options.headless:
		# 	# Extensions to solve ReCaptcha
		# 	options.add_extension("./extension/Captcha.crx")
		# 	options.add_extension("./extension/CORSon.crx")
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
		# driver=Chrome("./chromedriver.exe",options=options)
		# Windows 
		driver=Chrome(ChromeDriverManager().install(),options=options)
		return driver
	
	def start_driver(self,url, meeting_id, meeting_pwd):
		print("\nZoomPlusPlus Backend (Host)\n")
		if join_meeting(self.driver, url, meeting_id, meeting_pwd):
			# super().get_participants_list()
			# self.raised_hands_list = super().get_curr_reaction_list("raise_hands",self.raised_hands_list)
			# next_person , self.raised_hand_list = super().get_next_person_with_reaction(self.raised_hands_list)
			# super().send_message_next_person(next_person)
			# super().get_pictures()
			print("RETURN DRIVER")
			return self.driver
		else:
			print("Failed to start driver")
			return None

if __name__ == '__main__':
	backend = ZoomBackend(False)
	meeting_id = "9323412234" # Enter meeting id
	meeting_pwd = "1" # Enter meeting pwd
	backend.start_driver(None,meeting_id,meeting_pwd)