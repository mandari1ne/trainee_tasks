from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3 as sql
from datetime import datetime


# class for db connection
class DB:
    def __init__(self, db: str):
        self.db = db
        self.connection = sql.connect(db)

    def get_name_of_tables(self):
        '''
        getting name of tables
        '''

        with self.connection:
            cur = self.connection.execute('''
                SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ''')

            self.tables = [row[0] for row in cur.fetchall()]

            return self.tables

    def get_table_data(self, table_name):
        '''
        getting info from selected table
        '''

        with self.connection:
            cur = self.connection.execute(f'''
                SELECT * FROM {table_name}
            ''')

            data = cur.fetchall()

            return data

    def get_table_columns(self, table_name):
        '''
        getting column info of selected table
        '''

        with self.connection:
            cur = self.connection.execute(f"Pragma table_info ({table_name})")
            column_info = cur.fetchall()

            return column_info

    def update_table_data(self, table_name, id, column_name, new_value):
        '''
        update table row
        '''

        with self.connection:
            self.connection.execute(f'''
                UPDATE {table_name} SET {column_name} = {new_value} WHERE id = {id} 
            ''')

            self.connection.commit()


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()

        # list of modified cells (row, col)
        self.modified_cells = set()

    def setupUi(self, MainWindow, db=None):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(891, 614)
        MainWindow.setStyleSheet("background-color: rgb(219, 243, 255);")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 100, 871, 391))
        self.tableWidget.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                       "font-size: 20px;")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.tableWidget.itemChanged.connect(self.handle_modified)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(10, 500, 871, 71))
        self.lineEdit.setStyleSheet("color: rgb(255, 0, 0);\n"
                                    "background-color: rgb(237, 252, 255);\n"
                                    "font-size: 18px;")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 40, 291, 41))
        self.comboBox.setStyleSheet("background-color: rgb(188, 249, 255);\n"
                                    "font-size: 20px;")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("Название таблицы")
        self.comboBox.setItemData(0, 0, QtCore.Qt.UserRole - 1)
        self.comboBox.addItems(db.get_name_of_tables())

        self.comboBox.currentTextChanged.connect(self.get_table_info)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(530, 40, 81, 41))
        self.pushButton.setStyleSheet("background-color: rgb(188, 249, 255);\n"
                                      "font-size: 20px;")
        self.pushButton.setObjectName("pushButton")

        self.pushButton.clicked.connect(self.save)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(620, 40, 81, 41))
        self.pushButton_2.setStyleSheet("background-color: rgb(188, 249, 255);\n"
                                        "font-size: 20px;")
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton_2.clicked.connect(self.add_table_row)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(710, 40, 81, 41))
        self.pushButton_3.setStyleSheet("background-color: rgb(188, 249, 255);\n"
                                        "font-size: 20px;")
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_3.clicked.connect(self.reset_info)

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(800, 40, 81, 41))
        self.pushButton_4.setStyleSheet("background-color: rgb(188, 249, 255);\n"
                                        "font-size: 20px;")
        self.pushButton_4.setObjectName("pushButton_4")

        self.pushButton_4.clicked.connect(self.delete_selected_rows)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 891, 18))
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
        self.pushButton_2.setText(_translate("MainWindow", "+"))
        self.pushButton_3.setText(_translate("MainWindow", "Reset"))
        self.pushButton_4.setText(_translate("MainWindow", "-"))

    def get_table_info(self):
        '''
        getting selected table info
        '''

        self.lineEdit.clear()

        table = self.comboBox.currentText()
        table_data = db.get_table_data(table)
        columns_name = [col[1] for col in db.get_table_columns(table)]

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

    def add_table_row(self):
        '''
        for adding new table row
        '''

        if self.comboBox.currentText() == 'Название таблицы':
            self.lineEdit.setStyleSheet("color: red;")
            self.lineEdit.setText('Выберите название таблицы')
        else:
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)

    def reset_info(self):
        '''
        reset unsaved info
        '''

        if self.comboBox.currentText() == 'Название таблицы':
            self.lineEdit.setStyleSheet("color: red;")
            self.lineEdit.setText('Выберите название таблицы')
        else:
            self.get_table_info()

    def delete_selected_rows(self):
        '''
        delete selected table row without saving
        '''

        if self.comboBox.currentText() == 'Название таблицы':
            self.lineEdit.setStyleSheet("color: red;")
            self.lineEdit.setText('Выберите название таблицы')
        else:
            selected_rows = {index.row() for index in self.tableWidget.selectedIndexes()}

            if not selected_rows:
                self.lineEdit.setStyleSheet("color: red;")
                self.lineEdit.setText('Выберите строки в таблице')
            else:
                # delete from the end so that the indexes don't move
                for row in sorted(selected_rows, reverse=True):
                    self.tableWidget.removeRow(row)

    def handle_modified(self, item):
        '''
        add modified item into the modified list
        '''

        row, col = item.row(), item.column()
        self.modified_cells.add((row, col))

    def save(self):
        '''
        save table changes
        '''

        if self.comboBox.currentText() == 'Название таблицы':
            self.lineEdit.setStyleSheet("color: red;")
            self.lineEdit.setText('Выберите название таблицы')
        else:
            table_name = self.comboBox.currentText()
            columns_info = db.get_table_columns(table_name)
            errors = []

            for row, col in self.modified_cells:
                column_info = columns_info[col]
                column_name = column_info[1]
                column_type = column_info[2].upper()
                not_null = column_info[3]
                pk = column_info[5]

                if pk:
                    continue

                item = self.tableWidget.item(row, col)
                value = item.text() if item else ''

                if not_null and value == '':
                    errors.append(f'Строка {row + 1}, колонка "{column_name}": значение не должно быть пустым')
                    continue

                if value:
                    try:
                        if 'INT' in column_type:
                            int(value)
                        elif 'REAL' in column_type or 'FLOAT' in column_type or 'DOUBLE' in column_type:
                            float(value)
                        elif 'BOOLEAN' in column_type:
                            if value.upper() not in ('0', '1', 'TRUE', 'FALSE'):
                                raise ValueError
                        elif 'DATE' in column_type:
                            datetime.strptime(value, '%Y-%m-%d')
                        elif 'TIME' in column_type:
                            datetime.strptime(value, '%H:%M:%S')
                        elif 'DATETIME' in column_type or 'TIMESTAMP' in column_type:
                            datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    except ValueError as ve:
                        if 'DATE' in column_type or 'TIME' in column_type or 'DATETIME' in column_type:
                            errors.append(
                                f'Строка {row + 1}, колонка "{column_name}": неверный формат. Ожидается {column_type}')
                        else:
                            errors.append(
                                f'Строка {row + 1}, колонка "{column_name}": неверный тип. Ожидается {column_type}')

            if errors:
                self.lineEdit.setText('\n'.join(errors))
            else:
                try:
                    for row, col in self.modified_cells:
                        row_id = self.tableWidget.item(row, 0).text()
                        column_name = columns_info[col][1]
                        column_type = columns_info[col][2].upper()
                        item = self.tableWidget.item(row, col)
                        new_value = item.text() if item else ''

                        if new_value == '':
                            formatted_value = 'NULL'
                        elif 'INT' in column_type or 'BOOLEAN' in column_type:
                            formatted_value = new_value
                        elif 'REAL' in column_type or 'FLOAT' in column_type or 'DOUBLE' in column_type:
                            formatted_value = new_value
                        elif 'DATE' in column_type or 'TIME' in column_type or 'DATETIME' in column_type or 'TIMESTAMP' in column_type:
                            formatted_value = f"'{new_value}'"
                        else:  # TEXT, VARCHAR and other string types
                            # Proper escaping for SQL strings
                            escaped_value = new_value.replace("'", "''")
                            formatted_value = f"'{escaped_value}'"

                        db.update_table_data(table_name, row_id, column_name, formatted_value)

                    self.lineEdit.setStyleSheet("color: green;")
                    self.lineEdit.setText('Сохранено успешно')
                    self.modified_cells.clear()
                except Exception as e:
                    self.lineEdit.setText(f'Ошибка при сохранении: {str(e)}')


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    db = DB('warehouse.db')

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, db)

    MainWindow.show()
    sys.exit(app.exec_())
