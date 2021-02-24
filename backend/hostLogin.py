from selenium.webdriver.support.ui import WebDriverWait

from time import sleep, time
import pickle
import sys, traceback
from twocaptcha import TwoCaptcha
from re import findall

def is_page_loaded(driver):
	page_state = driver.execute_script('return document.readyState;' )
	return page_state == 'complete'

def wait_page_to_load(driver):
	sleep(1)
	while (not is_page_loaded(driver)):
		sleep(1)

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

	return False

RECAPTCHA_APPEARED = False
API_KEY ="26ae9da2b397fbcffcbb82a9e8f575d7"

def solveCaptcha(driver ):
	global RECAPTCHA_APPEARED
	st = time()
	print("Solving Captcha...")
	solver = TwoCaptcha(API_KEY)
	try:
		balance = solver.balance()
		if balance == 0:
			print("Account Balance is 0")
			driver.quit()
			sys.exit()
	except twocaptcha.api.ApiException:
		print("Invalid 2Captcha API_KEY")
		driver.quit()
		sys.exit()
		
	def get_sitekey(driver):
		sitekey = None
		found_captcha = False
		print("Find captcha")
		wait_5_secs = 0
		while not found_captcha : 
			if wait_5_secs == 5 :
				print("Could not find captcha")
				break
			if is_logged_in(driver):
				print("Break coz is_logged_in")
				break
			try: 
				recaptcha = driver.find_element_by_class_name("g-recaptcha")
				found_captcha = True 
				sitekey = recaptcha.get_attribute("data-sitekey")
				print(f"Got sitekey {sitekey}")
			except: 
				sleep(1) 
				wait_5_secs +=1
				print(wait_5_secs)
		
		return sitekey

	def form_submit(driver, token):
		# driver.execute_script("token='" + token + "'")
		# driver.execute_script("document.getElementById(\"g-recaptcha-response\").innerHTML=token")
		# driver.execute_script("_grecaptchaCallback(token)")
		driver.execute_script(f'document.querySelector(".g-recaptcha-response").innerText="{token}";')
		sleep(1)
	
	sitekey = get_sitekey(driver)
	if sitekey is not None and not is_logged_in(driver):
		print("Solving Captcha.....")
		result = solver.recaptcha(sitekey= sitekey, url=driver.current_url, version="v2")
		# if not Debug:
		print(result)
		form_submit(driver, result["code"])
		RECAPTCHA_APPEARED = True
		print("Solved captcha!! Takes " + str(time() - st) + " seconds")
		# elif Debug:
		# print("debug return")
		return result
	else:
		print("Exit solveCaptcha")


def login(driver):

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
	
	# sleep(3)

	# # Wait for the login authentication process			
	# wait = False if is_logged_in(driver) else True
	# while (wait):
	# 	sleep(1)
	# 	if(is_logged_in(driver)):
	# 		wait = False
	if not is_logged_in(driver):
		solveCaptcha(driver)

	save_cookies(driver)
	return True

# Join_meeting includes login, inserting name and password
def join_meeting(driver,room_link, meeting_id, meeting_pwd):
	if room_link:
		link_str = ''.join([i for i in room_link if i.isdigit()])
		zoom_meeting_id, zoom_meeting_pwd = link_str[0:11], link_str[11:]
	else:
		zoom_meeting_id = meeting_id
		zoom_meeting_pwd = meeting_pwd
	zoom_meeting_url = f"https://zoom.us/wc/join/{zoom_meeting_id}"
	
	driver.get("https://zoom.us/account")
	wait_page_to_load(driver)

	if( not is_logged_in(driver)):
		print("Have not logged in.Please wait...")
		login(driver)

	driver.get(zoom_meeting_url)
	load_cookies(driver)
	wait_page_to_load(driver)
	
	print("Finding name to insert to zoom meeting...")
	name_input_box = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("inputname"))
	name_join_button = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("joinBtn"))
	if(name_input_box[0].get_attribute('value') == ""):
		name = "Zoom PlusPlus"
		name_input_box[0].send_keys(name)
	print("Found the button")
	print(RECAPTCHA_APPEARED)
	if RECAPTCHA_APPEARED:
		click_i_m_not_robot(driver)
	name_join_button[0].click()
	print("Click name join button")

	wait_page_to_load(driver)

	try:
		print("Finding password to input to zoom meeting..")
		pwd_input_box = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("inputpasscode"))
		pwd_join_button = WebDriverWait(driver,15).until(lambda x: x.find_elements_by_id("joinBtn"))
		print("Found the button")
		pwd_input_box[0].send_keys(meeting_pwd)
		pwd_join_button[0].click()
		print("Click password join button")
	except:
		print("Could not find password")
		# TODO: UI should do something if meeting has not started
		try:
			print("Check if meeting has not started")
			meeting_status = driver.find_element_by_id("prompt")
			meeting_status = meeting_status.find_element_by_tag_name("h4")
			meeting_status = meeting_status.get_attribute("innerHTML")
			print(f"Meeting status: {meeting_status}")
			return False
		except:
			print("No password")
			pass

	wait_page_to_load(driver)
	sleep(3)
	found_button = False
	print("Find and click join audio button")
	while not found_button: 
		try: 
			join_audio_button = driver.find_element_by_xpath("//button[@class='zm-btn join-dialog__close zm-btn--default zm-btn__outline--blue']")
			join_audio_button.click() 
			found_button = True 
		except: 
			sleep(1) 
	
	save_cookies(driver)
	return True

def click_i_m_not_robot(driver):
	url = driver.current_url
	data_sitekey = None
	page_source = driver.page_source
	print("Done page source")
	data_sitekeys = findall('data-sitekey="(.*?)"', page_source)
	if data_sitekeys:
		data_sitekey = data_sitekeys[0]
		print("Multiple data sitekey selected the ffirst one")
	else:
		elments = driver.find_elements_by_xpath('//iframe[contains(@role,"presentation")]')
		print("in ifrmae")
		if elments:
			for elm in elments:
				if elm.is_displayed():
					src = elm.get_attribute('src')
					data_sitekey = findall('k=(.*?)&', src)[0]
					print(f"Data_stirekey is {data_sitekey}")
					break
		else:
			print("Did not find iframe")

	if data_sitekey is not None:
		solver = TwoCaptcha(API_KEY)
		sucess_id = solver.recaptcha(data_sitekey, url)

		driver.execute_script('document.querySelector(".g-recaptcha-response").style.display="block";')
		sleep(5)
		driver.execute_script('document.querySelector(".g-recaptcha-response").innerText="%s";' % sucess_id["code"])

		sleep(3)
		if driver.find_elements_by_xpath('//div[@data-callback]'):
			data_callback = driver.find_element_by_xpath('//div[@data-callback]').get_attribute('data-callback')
			driver.execute_script(data_callback + "();")
	else:
		print("Data_sitekey is none")