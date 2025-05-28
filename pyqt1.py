from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(810, 600)
        MainWindow.setStyleSheet(
            "QWidget{\n"
            "    background-color: rgb(183, 242, 255);\n"
            "}"
        )

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # insert button
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(260, 470, 81, 71))
        self.pushButton.setStyleSheet(
            "QPushButton {\n"
            "    background-color: rgb(255, 255, 255);\n"
            "     font-size: 20px;\n"
            "}"
        )
        self.pushButton.setObjectName("pushButton")

        # connect to function for insert item
        self.pushButton.clicked.connect(self.insert_item_into_list)

        # input lable
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(220, 350, 371, 51))
        self.lineEdit.setStyleSheet(
            "QLineEdit {\n"
            "    background-color: rgb(255, 255, 255);\n"
            "    font-size: 20px;\n"
            "}"
        )

        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")

        # delete button
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(470, 470, 81, 71))
        self.pushButton_2.setStyleSheet(
            "QPushButton {\n"
            "    background-color: rgb(255, 255, 255);\n"
            "     font-size: 20px;\n"
            "}"
        )
        self.pushButton_2.setObjectName("pushButton_2")

        # connect to function for delete item
        self.pushButton_2.clicked.connect(self.delete_item_from_list)

        # list items
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(190, 10, 431, 301))
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listWidget.setStyleSheet(
            "QListWidget {\n"
            "    background-color:  rgb(255, 255, 255);\n"
            "     color: rgb(0, 0, 255);\n"
            "    font-size: 20px;\n"
            "}\n"
            "\n"
            "QListWidget::item:selected {\n"
            "    background-color: #0078d7; \n"
            "}"
        )
        self.listWidget.setObjectName("listWidget")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 810, 18))
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
        self.pushButton.setText(_translate("MainWindow", "+"))
        self.pushButton_2.setText(_translate("MainWindow", "-"))

    # for inserting data
    def insert_item_into_list(self):
        self.listWidget.addItem(self.lineEdit.text())

    # for deleting data
    def delete_item_from_list(self):
        # get selected item
        selected_items = self.listWidget.selectedItems()

        if selected_items:
            for item in selected_items:
                self.listWidget.takeItem(self.listWidget.row(item))

        else:
            last_row = self.listWidget.count() - 1
            self.listWidget.takeItem(last_row)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
