from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: rgb(166, 236, 255);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton_warehouses = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_warehouses.setGeometry(QtCore.QRect(70, 80, 661, 51))
        self.pushButton_warehouses.setStyleSheet("background-color: rgb(255, 221, 133);\n"
                                                 "font-size: 30px;")
        self.pushButton_warehouses.setObjectName("pushButton_warehouses")

        self.pushButton_categories = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_categories.setGeometry(QtCore.QRect(70, 160, 661, 51))
        self.pushButton_categories.setStyleSheet("background-color: rgb(255, 221, 133);\n"
                                                 "font-size: 30px;")
        self.pushButton_categories.setObjectName("pushButton_categories")

        self.pushButton_employees = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_employees.setGeometry(QtCore.QRect(70, 240, 661, 51))
        self.pushButton_employees.setStyleSheet("background-color: rgb(255, 221, 133);\n"
                                                "font-size: 30px;")
        self.pushButton_employees.setObjectName("pushButton_employees")

        self.pushButton_clients = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_clients.setGeometry(QtCore.QRect(70, 320, 661, 51))
        self.pushButton_clients.setStyleSheet("background-color: rgb(255, 221, 133);\n"
                                              "font-size: 30px;")
        self.pushButton_clients.setObjectName("pushButton_clients")

        self.pushButton_results = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_results.setGeometry(QtCore.QRect(70, 400, 661, 51))
        self.pushButton_results.setStyleSheet("background-color: rgb(255, 221, 133);\n"
                                              "font-size: 30px;")
        self.pushButton_results.setObjectName("pushButton_results")

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
        self.pushButton_warehouses.setText(_translate("MainWindow", "Склады"))
        self.pushButton_categories.setText(_translate("MainWindow", "Категории товаров"))
        self.pushButton_employees.setText(_translate("MainWindow", "Сотрудники"))
        self.pushButton_clients.setText(_translate("MainWindow", "Клиенты"))
        self.pushButton_results.setText(_translate("MainWindow", "Итоги"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
