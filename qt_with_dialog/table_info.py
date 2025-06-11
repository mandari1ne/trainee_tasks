from PyQt5 import QtCore, QtGui, QtWidgets
import dialog


class Ui_MainWindow(object):
    def __init__(self):
        self.new_table_row = {}
        self.deleted_row = set()
        self.changed_rows = set()

        # {row_index: {col_name: value}}
        self.original_table_info = {}

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
        self.tableWidget.cellClicked.connect(self.get_row_details)
        self.verticalLayout.addWidget(self.tableWidget)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.horizontalLayout.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setStyleSheet("font-size: 22px;")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.save)
        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setStyleSheet("font-size: 22px;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.add_table_row)
        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setStyleSheet("font-size: 22px;")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.delete_selected_row)
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

    def get_table_info(self, table_name, db_):
        self.table = table_name
        self.db = db_

        self.new_table_row.clear()
        self.deleted_row.clear()
        self.changed_rows.clear()
        self.original_table_info.clear()

        table_data = db_.get_table_data(self.table)
        columns_name = [col[1] for col in self.db.get_table_columns(self.table)]

        self.tableWidget.blockSignals(True)

        self.tableWidget.setColumnCount(len(columns_name))
        self.tableWidget.setRowCount(len(table_data))
        self.tableWidget.setHorizontalHeaderLabels(columns_name)

        for row_index, row_data in enumerate(table_data):
            if row_index not in self.original_table_info:
                self.original_table_info[row_index] = {}
            for col_index, value in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(value))

                # blocked id column
                if col_index == 0:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                    item.setForeground(QtGui.QColor(100, 100, 100))

                self.tableWidget.setItem(row_index, col_index, item)

                self.original_table_info[row_index][columns_name[col_index]] = str(value)

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

    def delete_selected_row(self):
        selected_rows = {index.row() for index in self.tableWidget.selectedIndexes()}

        # delete from the end so that the indexes don't move
        for row in sorted(selected_rows, reverse=True):
            row_id_item = self.tableWidget.item(row, 0)
            # save id of deleted row
            if row_id_item:
                self.deleted_row.add((self.table, row_id_item.text()))

            self.tableWidget.removeRow(row)

    def get_row_details(self, row, column):
        row_data = {}
        columns_info = self.db.get_table_columns(self.table)
        column_names = [col[1] for col in columns_info]

        for col_index, col_name in enumerate(column_names):
            item = self.tableWidget.item(row, col_index)
            value = item.text() if item else ''

            row_data[col_name] = value if value else None

        dialog_ = dialog.Ui_Dialog(self.table, self.db)
        dialog_.set_row_data(row_data)
        result = dialog_.exec_()

        if result:
            updated_data = dialog_.result_data
            for col_index, (col_name, value) in enumerate(updated_data.items()):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.tableWidget.setItem(row, col_index, item)

            row_id_item = self.tableWidget.item(row, 0)
            if row_id_item and row_id_item.text():
                self.changed_rows.add(row)
            else:
                self.new_table_row[row] = updated_data

    def delete_row(self):
        for table, row in self.deleted_row:
            self.db.delete_row(table, row)
        self.deleted_row.clear()

    def insert_new_row(self):
        for row_index, row_data in self.new_table_row.items():
            try:
                row_insert = {k: v for k, v in row_data.items() if k.lower() != 'id'}
                self.db.insert_data(self.table, row_insert)
            except Exception as e:
                self.statusbar.setStyleSheet('color: red;')
                self.statusbar.showMessage('Ошибка сохранения', 3000)

        self.new_table_row.clear()

    def save(self):
            try:
                self.delete_row()
                self.insert_new_row()

                self.statusbar.setStyleSheet('color: green;')
                self.statusbar.showMessage('Сохранено успешно', 3000)
            except Exception as e:
                self.statusbar.setStyleSheet('color: red;')
                self.statusbar.showMessage('Ошибка сохранения', 3000)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
