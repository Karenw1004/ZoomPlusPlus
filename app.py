from PyQt5.QtCore import pyqtSignal, QCoreApplication, QObject, QThread
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QMessageBox, QDialog, QTabWidget, \
    QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtCore import pyqtSignal, QCoreApplication, pyqtSlot
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
import sys
from host import ZoomBackend
from backend.hostVideo import ZoomVideo
from time import sleep
import io
from PIL import Image
import cv2
import numpy as np
import re
import threading
import queue
from speech_to_text.speech_to_text import transcribe

def ceil(a, b):
    return -(-a // b)

def show_captions(img, text, max_characters_per_line=40):
    height, width = img.shape[:2]
    
    fontface = cv2.FONT_HERSHEY_DUPLEX
    fontscale = 0.7
    fontcolor = (0, 0, 255)

    number_of_lines = ceil(len(text), max_characters_per_line)
    # max_number_of_lines = 4
    
    for line in range(number_of_lines):
        line_text = text[max_characters_per_line*line: max_characters_per_line*line+max_characters_per_line]
        textSize = cv2.getTextSize(line_text, fontFace=fontface, fontScale=fontscale, thickness=1)
        center_displacement = np.array([int((width-textSize[0][0])/2)+textSize[0][0], (textSize[0][1]*2*(number_of_lines - line))])
        cv2.putText(img, line_text, (width-center_displacement[0],height-center_displacement[1]), fontface, fontscale, fontcolor, thickness=1)
    return img


# Step 1: Create a worker class
class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, id, pwd, url, parent=None):
        QThread.__init__(self, parent)
        self.meetingId = id
        self.password = pwd
        self.url = url

    def run(self):
        linkFunc(self.meetingId, self.password, self.url)
        self.finished.emit()


class LoadingButton(QPushButton):
    # @QtCore.pyqtSlot()
    def start(self):
        if hasattr(self, "_movie"):
            self._movie.start()

    # @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            self.setIcon(QtGui.QIcon())

    def setGif(self, filename):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setFileName(filename)
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frameNumber):
        self.setIcon(QtGui.QIcon(self._movie.currentPixmap()))


class loginWindow(QDialog):
    def __init__(self, q):
        super().__init__()
        self.login = uic.loadUi("./UI/xml/login_window.ui")
        self.meetingId = None
        self.password = None
        self.url = None
        self.mainWindow = None

        # self.pushButton_login = QPushButton("Join Meeting")
        # self.spinner = QtWaitingSpinner(self, disableParentWhenSpinning=True)
        # self.login.gridLayout.addWidget(self.pushButton_login)
        # self.login.gridLayout.addWidget(self.spinner)

        self.pushButton_login = LoadingButton("Join Meeting")
        self.pushButton_login.setGif("./UI/images/loading.gif")

        self.login.gridLayout.addWidget(self.pushButton_login)
        self.pushButton_login.clicked.connect(lambda: self.runLinkFunc(q))


    def getInfo(self):
        log = self.login.lineEdit_meeting_id.text().replace(" ", "")
        self.meetingId = log
        self.password = self.login.lineEdit_password.text()
        self.url = self.login.lineEdit_url.text()
        print(f"MeetingId: {self.meetingId}")
        print(f"password: {self.password}")
        print(f"url: {self.url}")

    def runLinkFunc(self,q):
        self.pushButton_login.start()

        # self.spinner.start()
        # self.pushButton_login.setText("Joining meeting..")
        self.getInfo()

        self.thread = QThread()
        self.worker = Worker(self.meetingId, self.password, self.url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        # Final resets
        self.pushButton_login.setEnabled(False)
        print("runLinkFUnc openMainWindow")
        self.thread.finished.connect(lambda: self.openMainWindow(q))

        print("after open main")

    def openMainWindow(self, q):
        self.login.hide()
        change_pixmap_signal = pyqtSignal(np.ndarray)

        self.mainWindow = MainWindow(backend)
        self.mainWindow.main.show()
        # self.mainWindow.createAttentionTable(10, 2, [])
        # self.mainWindow.createHandsTable(10, 1, [])
        # backend.get_participants_list()
        self.mainWindow.main.pushButton_next_question.clicked.connect(self.mainWindow.clear_hands_list)
        self.mainWindow.main.pushButton_next_student.clicked.connect(self.mainWindow.pop_hands_list)
        self.mainWindow.main.pushButton_test.clicked.connect(lambda:
                                                             self.mainWindow.createAttentionTable(10, 2,
                                                                                                  backend.get_participants_list()))

        vv = ZoomVideo(webdriver)
        vv.get_pictures()
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "./haarcascade_eye.xml")
        transcript = ""
        while True:
            image = webdriver.find_element_by_class_name("gallery-video-container__main-view").screenshot_as_png
            imageStream = io.BytesIO(image)
            im = Image.open(imageStream)
            img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
            # im.save("img2.png")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.06, 5)
            # print(faces)
            for (x,y,w,h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                # print(x, y, w, h)
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
                if len(eyes)==0:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, 'Not Attentive', (x,y-10), font, 0.5, (0,0,255), 1, cv2.LINE_AA)
                    img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
                else:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, 'Attentive', (x,y-10), font, 0.5, (0,255,0), 1, cv2.LINE_AA)
                    img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                for (ex,ey,ew,eh) in eyes:
                    # print(eyes)
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,0,111),2)

            if not q.empty():
                transcript = q.get()

            img = show_captions(img, transcript)

            cv2.imshow('face_feed',img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

class HandsTableThread(QThread):
    return_list_signal = pyqtSignal(list)

    def __init__(self, lst):
        super().__init__()
        self.hands_list = lst

    def run(self):
        while 1:
            self.sleep(3)
            self.hands_list = backend.get_curr_reaction_list("raise_hands", self.hands_list)
            if self.hands_list:
                self.return_list_signal.emit(self.hands_list)
            else:
                print("No raised hand from thread")


class MainWindow(QMainWindow):
    def __init__(self, backend_):
        super().__init__()
        self.main = uic.loadUi("./UI/xml/main_window.ui")
        self.table_student_attention = self.main.tableWidget_attention
        self.table_hands = self.main.tableWidget_hands
        self.num_student = self.main.label_student_number
        self.raised_hand_lbl = self.main.label_raised_hand_number
        self.first_student_lbl = self.main.label_first_student
        self.hands_list = []
        self.hands_table_thread = HandsTableThread(self.hands_list)
        self.hands_table_thread.return_list_signal.connect(self.createHandsTable)
        self.hands_table_thread.start()
        self.main.pushButton_test.clicked.connect(lambda: print("Test"))

    @pyqtSlot(np.ndarray)
    def update_image(self, img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(img)
        self.main.caption_feed.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def pop_hands_list(self):
        if self.hands_list:
            next_person = self.hands_list.pop()
            self.first_student_lbl.setText(next_person)
        self.createHandsTable(self.hands_list)
        print("call pop")

    def clear_hands_list(self):
        self.first_student_lbl.setText('None')
        if self.hands_list:
            self.hands_list.clear()
        self.createHandsTable(self.hands_list)
        print("call clear")

    def createAttentionTable(self, row, col, lst):
        # clear table
        self.table_student_attention.clear()
        # update student number label
        self.num_student.setText(str(len(lst)))
        # set row which is the number of students
        self.table_student_attention.setRowCount(row)
        # set col should be 2
        self.table_student_attention.setColumnCount(col)
        # set header
        self.table_student_attention.setHorizontalHeaderLabels(
            ['Name', 'Attention(%)'])
        # set everything in the lst, but I don't have list right now
        if not lst:
            for i in range(row):
                self.table_student_attention.setItem(
                    i, 0, QTableWidgetItem("cell" + str(i)))
                self.table_student_attention.setItem(
                    i, 1, QTableWidgetItem("cell" + str(i + 1)))
        else:
            for i in range(len(lst)):
                self.table_student_attention.setItem(i, 0, QTableWidgetItem(lst[i]))
                self.table_student_attention.setItem(
                    i, 1, QTableWidgetItem("No attention"))

        self.table_student_attention.horizontalHeader(
        ).setSectionResizeMode(QHeaderView.Stretch)

    def createHandsTable(self, lst):
        self.table_hands.clear()
        # updata label
        if lst:
            row = len(lst)
            # updata label
            self.raised_hand_lbl.setText(str(row))
            # set row
            self.table_hands.setRowCount(row)
            # set col = 1
            self.table_hands.setColumnCount(1)
            self.table_hands.setHorizontalHeaderLabels(["Raised hand students"])
            for i in range(row):
                self.table_hands.setItem(i, 0, QTableWidgetItem(lst[i]))
            self.table_hands.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.raised_hand_lbl.setText('0')
            print("No raised hand")


def linkFunc(id, pwd, url):
    headless = True
    global backend
    backend = ZoomBackend(headless)
    # declare webdriver to store chrome driver
    global webdriver
    # launch and store it (with the selected options)
    webdriver = backend.start_driver(url, id, pwd)
    driverStartFlag = True


if __name__ == '__main__':
    transcript = ""
    q = queue.Queue()
    t1= threading.Thread(target = transcribe, args=(transcript, q))

    t1.daemon = True
    t1.start() 

    app = QApplication(sys.argv)
    login = loginWindow(q)
    login.login.show()
    sys.exit(app.exec_())
