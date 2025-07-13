from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, name):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: rgb(166, 236, 255);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton_warehouses = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_warehouses.setGeometry(QtCore.QRect(70, 90, 661, 51))
        self.pushButton_warehouses.setStyleSheet("background-color: rgb(255, 221, 133);\n"
                                                 "font-size: 30px;")
        self.pushButton_warehouses.setText("")
        self.pushButton_warehouses.setObjectName("pushButton_warehouses")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 20, MainWindow.width(), 51))
        self.label.setStyleSheet("font-weight: bold;\n"
                                 "font-size: 40px")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.pushButton_add = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_add.setGeometry(QtCore.QRect(620, 30, 111, 41))
        self.pushButton_add.setStyleSheet("font-size: 20px;\n"
                                          "background-color: rgb(170, 170, 255);")
        self.pushButton_add.setObjectName("pushButton_add")

        if name == 'Клиенты' or name == 'Сотрудники':
            self.pushButton_delete = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_delete.setGeometry(QtCore.QRect(70, 30, 111, 41))
            self.pushButton_delete.setStyleSheet("font-size: 20px;\n"
                                                 "background-color: rgb(170, 170, 255);")
            self.pushButton_delete.setObjectName("pushButton_delete")
        else:
            self.pushButton_delete = None

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow, name)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow, name):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        # self.label.setText(_translate("MainWindow", "Склады"))
        self.label.setText(_translate("MainWindow", f"{name}"))
        self.pushButton_add.setText(_translate("MainWindow", "Добавить"))

        if self.pushButton_delete:
            self.pushButton_delete.setText(_translate("MainWindow", "Удалить"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, '')
    MainWindow.show()
    sys.exit(app.exec_())
