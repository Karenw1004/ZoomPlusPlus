from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager

from backend.hostLogin import join_meeting

def init_driver(headless):
	options = Options()
	options.headless = headless
	options.add_argument("--window-size=1600,1200")
	# List of options to avoid reCaptcha
	options.add_argument('--profile-directory=profile')
	options.add_argument("--disable-blink-features")
	options.add_argument("start-maximized")
	options.add_argument('--disable-gpu')
	options.add_argument('--no-sandbox')
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option('useAutomationExtension', False)
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_argument("--use-fake-ui-for-media-stream")
	options.add_argument(
	f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36')
	
	driver=Chrome(ChromeDriverManager().install(),options=options)
	return driver

def main():

	print("\nZoomPlusPlus Backend (Host)\n")
	driver = init_driver(False)
	join_meeting(driver)
	print("Done")

if __name__ == '__main__':
	main()