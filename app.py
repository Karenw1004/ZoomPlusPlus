from PyQt5 import uic
import sys
from host import ZoomBackend
from PyQt5.QtCore import pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QMessageBox, QDialog
import threading


class loginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.login = uic.loadUi("./UI/login_window.ui")
        self.meetingId = None
        self.password = None
        self.url = None
        self.mainWindow = MainWindow()
        self.login.pushButton_login.clicked.connect(self.openMainWindow)

    def getInfo(self):
        self.meetingId = self.login.lineEdit_meeting_id.text()
        self.password = self.login.lineEdit_password.text()
        self.url = self.login.lineEdit_url.text()
        print(self.meetingId)
        print(self.url)
        print(self.password)

    def openMainWindow(self):
        self.getInfo()
        self.mainWindow.main.show()
        print("after open main")
        linkFunc(self.meetingId, self.password, self.url)
        # web_thread = threading.Thread(target=linkFunc(self.meetingId, self.password, self.url))
        # web_thread.start()
        # web_thread.join()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main = uic.loadUi("./UI/main_window.ui")
        # self.main.pushButton_test.clicked.connect(lambda: print("testing"))


def linkFunc(id, pwd, url):
    # get selenium data collector going
    # set launch options
    # room_link = linkInputVal.get()

    # if not url:
    #     url = id + " " + pwd

    print("URL is ", url)
    headless = False
    backend = ZoomBackend(headless)
    # declare webdriver to store chrome driver
    global webdriver
    # launch and store it (with the selected options)
    webdriver = backend.start_driver(url, id, pwd)
    driverStartFlag = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = loginWindow()
    login.login.show()
    sys.exit(app.exec_())
