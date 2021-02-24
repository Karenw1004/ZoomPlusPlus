from time import sleep
import io
from PIL import Image
import cv2
import numpy

class ZoomVideo:
    def __init__(self, driver):
        self.driver = driver

    def get_pictures(self):
    
        found_button = False
        print("Click gallery view")
        while not found_button: 
            try: 
                view_button = self.driver.find_elements_by_xpath("//button[@class='full-screen-widget__button dropdown-toggle btn btn-default']")
                view_button[0].click() 
                gallery_view = self.driver.find_elements_by_xpath("//a[@aria-label='Gallery View']")
                gallery_view[0].click()
                found_button = True 
            except: 
                sleep(1) 
        
        found_gallery = False
        print("Try to take picture of gallery view")
        image = None
        while not found_gallery:
            try:
                gallery_square = self.driver.find_element_by_class_name("video-avatar__avatar")
                found_gallery = True 
            except:
                sleep(1)

        sleep(5) # wait for the gallery_square to load
        