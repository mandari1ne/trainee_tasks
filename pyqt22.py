from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3 as sql


class DB:
    def __init__(self, db: str):
        self.db = db
        self.connection = sql.connect(db)

    def get_name_of_tables(self):
        with self.connection:
            cur = self.connection.execute('''
                SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ''')

            self.tables = [row[0] for row in cur.fetchall()]

            return self.tables

    def get_table_columns(self, table_name):
        with self.connection:
            cur = self.connection.execute(f"Pragma table_info ({table_name})")
            column_info = cur.fetchall()

            return column_info

    def get_table_fk(self, table_name):
        with self.connection:
            cur = self.connection.execute(f"Pragma foreign_key_list ({table_name})")

            fks = cur.fetchall()

            # fk: {имя_столбца: (таблица, столбец)}
            return {fk[3]: (fk[2], fk[4]) for fk in fks}

    def get_related_value(self, fk_table, fk_col, fk_value):
        with self.connection:
            try:
                row = self.connection.execute(
                    f'SELECT * FROM {fk_table} WHERE {fk_col} = ?',
                    (fk_value,)
                ).fetchone()

                return row[1] if row else ""
            except sql.Error as e:
                print(f"Ошибка получения связанного значения: {e}")
                return ""

    def get_table_data(self, table_name):
        with self.connection:
            cur = self.connection.execute(f'''
                SELECT * FROM {table_name}
            ''')

            data = cur.fetchall()

            column_info = self.get_table_columns(table_name)
            column_names = [col[1] for col in column_info]

            fk_info = self.get_table_fk(table_name)

            processed_data = []
            for row in data:
                new_row = list(row)
                for col_idx, col_name in enumerate(column_names):
                    if col_name in fk_info:
                        fk_table, fk_col = fk_info[col_name]
                        fk_value = row[col_idx]

                        related_value = self.get_related_value(fk_table, fk_col, fk_value)

                        new_row[col_idx] = f"{fk_value}-{related_value}" if fk_value is not None else ""

                processed_data.append(tuple(new_row))

            return processed_data

    def insert_data(self, table_name, values):
        with self.connection:
            columns = ', '.join(values.keys())
            insert_value = ', '.join(['?'] * len(values))

            self.connection.execute(f'''
                INSERT INTO {table_name} ({columns}) VALUES ({insert_value})
            ''', tuple(values.values()))

            self.connection.commit()

    def delete_row(self, table_name, row_id):
        with self.connection:
            self.connection.execute(f'''
                DELETE FROM {table_name} WHERE id = ?
            ''', (row_id,))

            self.connection.commit()

    def update_row(self, table_name, row_id, values):
        with self.connection:
            update_value = ', '.join(f'{col} = ?' for col in values.keys())
            params = list(values.values()) + [row_id]

            self.connection.execute(f'''
                UPDATE {table_name} SET {update_value} WHERE id = ?
            ''', params)

            self.connection.commit()


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()

        self.new_table_row = {}
        self.deleted_row = set()
        self.changed_rows = set()

        # {row_index: {col_name: value}}
        self.original_table_info = {}

    def setupUi(self, MainWindow, db):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(891, 614)
        MainWindow.setStyleSheet("background-color: rgb(219, 243, 255);")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setStyleSheet("background-color: rgb(188, 249, 255);\n"
                                    "font-size: 20px;")
        self.comboBox.setFixedWidth(250)
        self.comboBox.setMinimumHeight(35)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("Название таблицы")
        self.comboBox.setItemData(0, 0, QtCore.Qt.UserRole - 1)
        self.horizontalLayout.addWidget(self.comboBox)
        self.comboBox.addItems(db.get_name_of_tables())

        self.comboBox.currentTextChanged.connect(self.get_table_info)

        self.horizontalLayout.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setStyleSheet("background-color: rgb(188, 249, 255); \n"
                                      "font-size: 20px;")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton.clicked.connect(self.save)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setStyleSheet("background-color: rgb(188, 249, 255); \n"
                                        "font-size: 20px;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_2.clicked.connect(self.add_table_row)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setStyleSheet("background-color: rgb(188, 249, 255); \n"
                                        "font-size: 20px;")
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)

        self.pushButton_3.clicked.connect(self.get_table_info)

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setStyleSheet("background-color: rgb(188, 249, 255); \n"
                                        "font-size: 20px;")
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.delete_selected_row)
        self.horizontalLayout.addWidget(self.pushButton_4)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setStyleSheet("background-color: rgb(255, 255, 255); \n"
                                       "font-size: 20px;")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)

        self.tableWidget.itemChanged.connect(self.on_item_changed)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setStyleSheet("color: rgb(255, 0, 0); \n"
                                    "background-color: rgb(237, 252, 255); \n"
                                    "font-size: 18px;")
        self.lineEdit.setMinimumHeight(80)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)

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

    def is_error(self, text):
        self.lineEdit.setText(text)

        text_errors = ['Не найдено', 'пустым',
                       'Некорректное значение в столбце',
                       'Выберите строки в таблице',
                       'Ошибка обновления',
                       'Ошибка FK']

        is_error = (
                self.comboBox.currentText() == 'Название таблицы' or
                any(keyword in text for keyword in text_errors)
        )

        color = "red" if is_error else "green"

        self.lineEdit.setStyleSheet(f"color: {color};")

        return is_error

    def validate_data(self, table_name, row_data):
        columns_info = db.get_table_columns(table_name)
        validated_data = row_data.copy()

        for col in columns_info:
            col_name = col[1]
            col_type = col[2].upper()
            is_nullable = not col[3]

            value = row_data.get(col_name)

            # if not null
            if not is_nullable and (value is None or str(value).strip() == ""):
                self.is_error(f"Столбец '{col_name}' не может быть пустым")

                return False, {}

            # if null
            if value is None or str(value).strip() == "":
                continue

            try:
                if 'INT' in col_type:
                    validated_data[col_name] = int(value)
                elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type or 'DECIMAL' in col_type:
                    validated_data[col_name] = float(value)
                elif 'BOOLEAN' in col_type:
                    if str(value).upper() not in ('0', '1', 'TRUE', 'FALSE'):
                        raise ValueError
                    validated_data[col_name] = str(value).upper() in ('1', 'TRUE')
            except ValueError:
                self.is_error(f"Некорректное значение в столбце '{col_name}'. "
                              f"Ожидается тип: {col_type}")
                return False, {}

        return True, validated_data

    def on_item_changed(self, item):
        self.changed_rows.add(item.row())

    def get_table_info(self):
        if self.comboBox.currentText() == 'Название таблицы' and self.is_error('Выберите таблицу'):
            return

        self.new_table_row.clear()
        self.deleted_row.clear()
        self.original_table_info.clear()
        self.changed_rows.clear()
        self.lineEdit.clear()

        table = self.comboBox.currentText()
        table_data = db.get_table_data(table)
        columns_name = [col[1] for col in db.get_table_columns(table)]

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
        if self.comboBox.currentText() == 'Название таблицы' and self.is_error('Выберите таблицу'):
            return

        self.lineEdit.clear()
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
        if self.comboBox.currentText() == 'Название таблицы' and self.is_error('Выберите таблицу'):
            return

        selected_rows = {index.row() for index in self.tableWidget.selectedIndexes()}

        if not selected_rows and self.is_error('Выберите строки в таблице'):
            return

        table_name = self.comboBox.currentText()

        # delete from the end so that the indexes don't move
        for row in sorted(selected_rows, reverse=True):
            row_id_item = self.tableWidget.item(row, 0)
            # save id of deleted row
            if row_id_item:
                self.deleted_row.add((table_name, row_id_item.text()))

            self.tableWidget.removeRow(row)

    def get_row_data(self, row_index, table_name):
        columns_info = db.get_table_columns(table_name)
        column_names = [col[1] for col in columns_info]

        fk_info = db.get_table_fk(table_name)

        row_data = {}
        for col_index, col_name in enumerate(column_names):
            item = self.tableWidget.item(row_index, col_index)
            value = item.text() if item else ''

            if col_name in fk_info:
                if '-' in value:
                    value = value.split('-')[0]
                elif value:
                    fk_table, fk_col = fk_info[col_name]
                    fk_cols = [c[1] for c in db.get_table_columns(fk_table)]
                    text_col = fk_cols[1]
                    result = db.connection.execute(
                        f"SELECT {fk_col} FROM {fk_table} WHERE {text_col} = ?",
                        (value,)
                    ).fetchone()
                    if result:
                        value = result[0]
                    else:
                        self.is_error(f"Ошибка FK: '{value}' не найдено в таблице '{fk_table}'")
                        return None

            row_data[col_name] = value if value else None

        return row_data

    def insert_new_row(self):
        table_name = self.comboBox.currentText()

        for row in list(self.new_table_row.keys()):
            row_data = self.get_row_data(row, table_name)

            if row_data is None:
                return

            is_valid, validated_data = self.validate_data(table_name, row_data)
            if is_valid:
                try:
                    db.insert_data(table_name, validated_data)
                    self.is_error('Сохранено успешно')
                except sql.Error as e:
                    self.is_error(f"Ошибка сохранения: {str(e)}")
            else:
                continue

    def delete_row(self):
        try:
            for table, row in self.deleted_row:
                db.delete_row(table, row)
                self.is_error('Удалено успешно')
            self.deleted_row.clear()
        except Exception as e:
            self.is_error(f'Ошибка удаления: {e}')

    def modified_row(self):
        table_name = self.comboBox.currentText()

        for row in self.changed_rows:
            current_data = self.get_row_data(row, table_name)
            if current_data is None:
                return

            original_data = self.original_table_info.get(row, {})

            changes = {col: current_data[col] for col in current_data
                       if str(current_data[col]) != str(original_data.get(col))}

            if changes:
                try:
                    row_id = current_data['id']
                    is_valid, validated_data = self.validate_data(table_name, current_data)
                    if is_valid:
                        changed_validated_data = {k: validated_data[k] for k in changes}
                        db.update_row(table_name, row_id, changed_validated_data)
                        self.is_error('Сохранено успешно')
                except Exception as e:
                    self.is_error(f'Ошибка обновления: {e}')

        self.changed_rows.clear()

    def save(self):
        if self.comboBox.currentText() == 'Название таблицы' and self.is_error('Выберите таблицу'):
            return

        self.insert_new_row()
        self.delete_row()
        self.modified_row()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    db = DB('warehouse.db')

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, db)

    MainWindow.show()
    sys.exit(app.exec_())
