from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def __init__(self):
        self.new_table_row = {}

        self.table = None
        self.db = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.horizontalLayout.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setStyleSheet("font-size: 22px;")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setStyleSheet("font-size: 22px;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.add_table_row)
        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setStyleSheet("font-size: 22px;")
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setStyleSheet("font-size: 22px;")
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(lambda: self.get_table_info(self.table, self.db))
        self.horizontalLayout.addWidget(self.pushButton_4)

        self.horizontalLayout.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.verticalLayout.addLayout(self.horizontalLayout)

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
        self.pushButton.setText(_translate("MainWindow", "Save"))
        self.pushButton_2.setText(_translate("MainWindow", "Add"))
        self.pushButton_3.setText(_translate("MainWindow", "Delete"))
        self.pushButton_4.setText(_translate("MainWindow", "Reset"))

    def get_table_info(self,  table_name, db_):
        self.table = table_name
        self.db = db_

        table_data = db_.get_table_data(self.table)
        columns_name = [col[1] for col in self.db.get_table_columns(self.table)]

        self.tableWidget.blockSignals(True)

        self.tableWidget.setColumnCount(len(columns_name))
        self.tableWidget.setRowCount(len(table_data))
        self.tableWidget.setHorizontalHeaderLabels(columns_name)

        for row_index, row_data in enumerate(table_data):
            for col_index, value in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(value))

                # blocked id column
                if col_index == 0:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                    item.setForeground(QtGui.QColor(100, 100, 100))

                self.tableWidget.setItem(row_index, col_index, item)

        self.tableWidget.blockSignals(False)

    def add_table_row(self):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        if row_position not in self.new_table_row:
            self.new_table_row[row_position] = ()

        # insert null values
        for col in range(self.tableWidget.columnCount()):
            item = QtWidgets.QTableWidgetItem('')

            if col == 0:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)

            self.tableWidget.setItem(row_position, col, item)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())