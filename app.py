from PyQt5.QtCore import pyqtSignal, QCoreApplication, QObject, QThread
from PyQt5 import QtCore, QtGui, QtWidgets
# from waitingspinnerwidget import QtWaitingSpinner
import threading
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QMessageBox, QDialog, QPushButton
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QMessageBox, QDialog, QTabWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSignal, QCoreApplication
from PyQt5 import uic
import sys
from host import ZoomBackend



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
    def __init__(self):
        super().__init__()
        self.login = uic.loadUi("./UI/xml/login_window.ui")
        self.meetingId = None
        self.password = None
        self.url = None
        self.mainWindow = MainWindow()

        # self.pushButton_login = QPushButton("Join Meeting")
        # self.spinner = QtWaitingSpinner(self, disableParentWhenSpinning=True)
        # self.login.gridLayout.addWidget(self.pushButton_login)
        # self.login.gridLayout.addWidget(self.spinner)

        self.pushButton_login = LoadingButton("Join Meeting")
        self.pushButton_login.setGif("./UI/images/loading.gif")

        self.login.gridLayout.addWidget(self.pushButton_login)
        self.pushButton_login.clicked.connect(self.runLinkFunc)

    def getInfo(self):
        self.meetingId = self.login.lineEdit_meeting_id.text()
        self.password = self.login.lineEdit_password.text()
        self.url = self.login.lineEdit_url.text()
        print(f"MeetingId: {self.meetingId}")
        print(f"password: {self.password}")
        print(f"url: {self.url}")

    def runLinkFunc(self):
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
        self.thread.finished.connect(lambda: self.openMainWindow())

        print("after open main")
        # web_thread = threading.Thread(target=linkFunc(self.meetingId, self.password, self.url))
        # web_thread.start()
        # web_thread.join()

    def openMainWindow(self):
        self.mainWindow.main.show()
        self.login.hide()
        self.mainWindow.createAttentionTable(10, 2, [])
        self.mainWindow.createHandsTable(10, 1, [])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main = uic.loadUi("./UI/xml/main_window.ui")
        self.table_student_attention = self.main.tableWidget_attention
        self.table_hands = self.main.tableWidget_hands
        self.main.pushButton_test.clicked.connect(lambda: print("testing"))

    def createAttentionTable(self, row, col, lst):
        # set row which is the number of students
        self.table_student_attention.setRowCount(row)
        # set col should be 2
        self.table_student_attention.setColumnCount(col)
        # set header
        self.table_student_attention.setHorizontalHeaderLabels(
            ['Name', 'Attention(%)'])
        # set everything in the lst, but I don't have list right now
        for i in range(row):
            self.table_student_attention.setItem(
                i, 0, QTableWidgetItem("cell"+str(i)))
            self.table_student_attention.setItem(
                i, 1, QTableWidgetItem("cell"+str(i+1)))
        self.table_student_attention.horizontalHeader(
        ).setSectionResizeMode(QHeaderView.Stretch)

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
