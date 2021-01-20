from selenium.webdriver.support.ui import WebDriverWait

from time import sleep
import pickle
import sys, traceback


def is_page_loaded(driver):
	page_state = driver.execute_script('return document.readyState;' )
	return page_state == 'complete'

def wait_page_to_load(driver):
	sleep(1)
	while (not is_page_loaded(driver)):
		sleep(2)

def load_cookies(driver):
		cookies = pickle.load(open("cookies.pkl", "rb"))
		for cookie in cookies:
			if 'expiry' in cookie:
				del cookie['expiry']
			try:
				driver.add_cookie(cookie)
			except:
				print("Failed to add cookies")
		return True

def save_cookies(driver):
	pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
	return True

def is_logged_in(driver):
	try:
		curr_url = driver.current_url
		if( "zoom" not in curr_url):
			print("Redirected away from zoom. Waiting to get back....")
			return False
		profile_url = driver.find_elements_by_xpath('//a[@href=\'http://zoom.us/profile\']')
		login_url = driver.find_elements_by_xpath('//a[@href=\'https://zoom.us/signin\']')
		signup_url = driver.find_elements_by_xpath('//a[@href=\'https://zoom.us/signup\']')
		if( (len(profile_url) > 0 or ("account" in curr_url) or ("profile" in curr_url) ) and (len(login_url) == 0 or len(signup_url) == 0) ):
			print("Successfully logged in !")
			return True

		print("Have not logged in.Please wait...")
		return False
	except:
		print("Unexpected error occured while checking login status")
		exit()


def login(driver):

	try:
		if(driver.current_url != "https://zoom.us/signin"):
			print(driver.current_url)
			driver.get("https://zoom.us/signin")

		# Login with email and pass for ZoomPlusPlus
		email = driver.find_element_by_id('email')
		password = driver.find_element_by_id('password')
		email.send_keys("no.reply.for.my.project@gmail.com")
		password.send_keys("Temp4321")
		login_button = driver.find_elements_by_xpath("//button[@class='btn btn-primary signin user']")
		login_button[0].click()

		# Wait for the login authentication process			
		wait = False if is_logged_in(driver) else True
		while (wait):
			sleep(1)
			if(is_logged_in(driver)):
				wait = False

		save_cookies(driver)
		return True
	except:
		print("Unexpected error occured during login process")
		exit()

# Join_meeting includes login, inserting name and password
def join_meeting(driver,room_link, meeting_id, meeting_pwd):
	if room_link:
		link_str = ''.join([i for i in room_link if i.isdigit()])
		zoom_meeting_id, zoom_meeting_pwd = link_str[0:11], link_str[11:]
	else:
		zoom_meeting_id = meeting_id
		zoom_meeting_pwd = meeting_pwd
	zoom_meeting_url = "https://zoom.us/wc/join/" + zoom_meeting_id
	
	url = f"https://zoom.us/j/{zoom_meeting_id}?pwd={zoom_meeting_pwd}"

	try:
		driver.get("https://zoom.us/account")
		load_cookies(driver)
		wait_page_to_load(driver)

		if( not is_logged_in(driver)):
			login(driver)

		driver.get(zoom_meeting_url)
		wait_page_to_load(driver)
		# TODO: MEETING HAS NOT STARTED ERROR 
		
		# Input the name to zoom meeting 
		name_input_box = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("inputname"))
		name_join_button = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("joinBtn"))
		if(name_input_box[0].get_attribute('value') == ""):
			name = input("Please Input your name here and press <enter> : ")
			name_input_box[0].send_keys(name)
		name_join_button[0].click()

		wait_page_to_load(driver)

		# Input zoom meeting pwd
		pwd_input_box = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("inputpasscode"))
		pwd_join_button = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("joinBtn"))
		pwd_input_box[0].send_keys(meeting_pwd)
		pwd_join_button[0].click()

	except KeyboardInterrupt:
		raise Exception("Keyboard Interrupt")
	except:
		traceback.print_exc(file=sys.stdout)
	finally:
		save_cookies(driver)