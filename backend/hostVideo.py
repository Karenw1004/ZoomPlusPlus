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
        print("Find gallery view")
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
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "./haarcascade_eye.xml")

        while True:
            image = self.driver.find_element_by_class_name("gallery-video-container__main-view").screenshot_as_png
            image_stream = io.BytesIO(image)
            im = Image.open(image_stream)
            opencv_image = cv2.cvtColor(numpy.array(im), cv2.COLOR_RGB2BGR)
            # im.save("img2.png")
            # print("success")
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(opencv_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = opencv_image[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                
            cv2.imshow('Face Feed',opencv_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break