from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: rgb(166, 236, 255);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(350, 50, 101, 41))
        self.label.setStyleSheet("font-size: 38px;\n"
                                 "font-weight: bold;")
        self.label.setObjectName("label")

        self.label_login = QtWidgets.QLabel(self.centralwidget)
        self.label_login.setGeometry(QtCore.QRect(240, 160, 61, 31))
        self.label_login.setStyleSheet("font-size: 24px;")
        self.label_login.setObjectName("label_login")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(240, 210, 111, 31))
        self.label_3.setStyleSheet("font-size: 24px")
        self.label_3.setObjectName("label_3")

        self.lineEdit_login = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_login.setGeometry(QtCore.QRect(360, 160, 241, 31))
        self.lineEdit_login.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                          "font-size: 20px;")
        self.lineEdit_login.setObjectName("lineEdit_login")

        self.lineEdit_password = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_password.setGeometry(QtCore.QRect(360, 210, 241, 31))
        self.lineEdit_password.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                      "font-size: 20px;")
        self.lineEdit_password.setText("")
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")

        self.pushButton_login = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_login.setGeometry(QtCore.QRect(340, 340, 121, 41))
        self.pushButton_login.setStyleSheet("background-color: rgb(23, 193, 255);\n"
                                            "font-size: 20px;")
        self.pushButton_login.setObjectName("pushButton_login")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Вход"))
        self.label_login.setText(_translate("MainWindow", "Login"))
        self.label_3.setText(_translate("MainWindow", "Password"))
        self.pushButton_login.setText(_translate("MainWindow", "Вход"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
