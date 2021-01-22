from PyQt5 import uic
import sys
from host import ZoomBackend
from PyQt5.QtCore import pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QMessageBox, QDialog, QTabWidget, QTableWidgetItem, QHeaderView
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
        self.mainWindow.createHandsTable(10, 1, [])
        self.mainWindow.createAttentionTable(15, 2, [])
        # linkFunc(self.meetingId, self.password, self.url)
        # web_thread = threading.Thread(target=linkFunc(self.meetingId, self.password, self.url))
        # web_thread.start()
        # web_thread.join()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main = uic.loadUi("./UI/main_window.ui")
        self.table_student_attention = self.main.tableWidget_attention
        self.table_hands = self.main.tableWidget_hands
        self.main.pushButton_test.clicked.connect(lambda: print("testing"))

    def createAttentionTable(self, row, col, lst):
        # set row which is the number of students
        self.table_student_attention.setRowCount(row)
        # set col should be 2
        self.table_student_attention.setColumnCount(col)
        # set header
        self.table_student_attention.setHorizontalHeaderLabels(['Name', 'Attention(%)'])
        # set everything in the lst, but I don't have list right now
        for i in range(row):
            self.table_student_attention.setItem(i, 0, QTableWidgetItem("cell"+str(i)))
            self.table_student_attention.setItem(i, 1, QTableWidgetItem("cell"+str(i+1)))
        self.table_student_attention.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def createHandsTable(self, row, col, lst):
        # set row
        self.table_hands.setRowCount(row)
        # set col should be 1
        self.table_hands.setColumnCount(col)
        self.table_hands.setHorizontalHeaderLabels(["Raised hand students"])
        for i in range(row):
            self.table_hands.setItem(i, 0, QTableWidgetItem("student"+str(i)))
        self.table_hands.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


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
