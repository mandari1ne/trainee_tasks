from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setObjectName("Dialog")
        self.resize(400, 300)
        self.setStyleSheet("background-color: rgb(255, 176, 144);")

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(140, 250, 121, 32))
        self.buttonBox.setStyleSheet("font-size: 16px;\n"
                                     "background-color: rgb(170, 170, 255);")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 40, 371, 31))
        self.label.setStyleSheet("font-size: 25px;\n"
                                 "font-weight: bold;")
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(30, 90, 341, 31))
        self.lineEdit.setStyleSheet("font-size: 16px;\n"
                                    "background-color: rgb(255, 255, 255);")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(170, 220, 71, 21))
        self.label_2.setStyleSheet("font-size: 15px")
        self.label_2.setObjectName("label_2")

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept)  # type: ignore
        self.buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Введите имя для удаления:"))
        self.label_2.setText(_translate("Dialog", "Удалить?"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Dialog()
    ui.show()
    sys.exit(app.exec_())
