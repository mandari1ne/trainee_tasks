from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setObjectName("Dialog")
        self.resize(400, 300)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.details_label_container = QtWidgets.QWidget(self)
        self.details_layout = QtWidgets.QVBoxLayout(self.details_label_container)
        self.details_label_container.setLayout(self.details_layout)
        self.main_layout.addWidget(self.details_label_container)
        self.main_layout.addStretch(1)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(-70, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.buttonBox)
        self.button_layout.addStretch(1)
        self.main_layout.addLayout(self.button_layout)

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore

        self.line_edits = {}
        self.original_row_data = {}

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))

    def set_row_data(self, row_data):
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.line_edits.clear()
        self.original_row_data = row_data.copy()

        for col_name, value in row_data.items():
            row_h_layout = QtWidgets.QHBoxLayout()

            name_label = QtWidgets.QLabel(f'{col_name}:', self)
            name_label.setStyleSheet("font-size: 16px;")
            name_label.setFixedWidth(120)

            line_edit = QtWidgets.QLineEdit(str(value), self)
            line_edit.setStyleSheet('font-size: 16px;')

            if col_name.lower() == 'id':
                line_edit.setReadOnly(True)
                line_edit.setStyleSheet(
                    'font-size: 16px; background-color: #f0f0f0;')

            row_h_layout.addWidget(name_label)
            row_h_layout.addWidget(line_edit)

            self.details_layout.addLayout(row_h_layout)

            self.line_edits[col_name] = line_edit

        self.details_layout.addStretch(1)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    ui = Ui_Dialog()

    ui.show()
    sys.exit(app.exec_())
