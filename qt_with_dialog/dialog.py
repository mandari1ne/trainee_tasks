from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self, table_name, db):
        super().__init__()

        self.table_name = table_name
        self.db = db

        self.setObjectName("Dialog")
        self.resize(400, 300)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.details_label_container = QtWidgets.QWidget(self)
        self.details_layout = QtWidgets.QVBoxLayout(self.details_label_container)
        self.details_label_container.setLayout(self.details_layout)
        self.main_layout.addWidget(self.details_label_container)
        self.main_layout.addStretch(1)

        self.error_label = QtWidgets.QLabel(self)
        self.error_label.setStyleSheet("color: red; font-size: 14px;")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        # self.error_label.setVisible(False)
        self.main_layout.addWidget(self.error_label)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(-70, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.buttonBox)
        self.button_layout.addStretch(1)
        self.main_layout.addLayout(self.button_layout)

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept)  # type: ignore
        self.buttonBox.rejected.connect(self.reject)  # type: ignore

        self.line_edits = {}
        self.original_row_data = {}
        self.result_data = None

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

            if not value:
                line_edit = QtWidgets.QLineEdit('', self)
            else:
                line_edit = QtWidgets.QLineEdit(str(value), self)

            line_edit.setStyleSheet('font-size: 16px;')

            if col_name.lower() == 'id':
                line_edit.setReadOnly(True)
                line_edit.setStyleSheet('font-size: 16px; '
                                        'background-color: #f0f0f0;')

            row_h_layout.addWidget(name_label)
            row_h_layout.addWidget(line_edit)

            self.details_layout.addLayout(row_h_layout)

            self.line_edits[col_name] = line_edit

        self.details_layout.addStretch(1)

    def get_current_data(self):
        data = {}
        fk_info = self.db.get_table_fk(self.table_name)

        for col_name, value in self.line_edits.items():
            value_text = value.text()

            if col_name in fk_info:
                if '-' in value_text:
                    value_text = value_text.split('-')[0]
                elif value_text:
                    fk_table, fk_col = fk_info[col_name]
                    fk_cols = [c[1] for c in self.db.get_table_columns(fk_table)]
                    text_col = fk_cols[1]

                    try:
                        result = self.db.connection.execute(f'''
                            SELECT {fk_col} FROM {fk_table} WHERE {text_col} = ?
                        ''', (value_text,)).fetchone()
                        value_text = result[0]
                    except TypeError:
                        self.is_error(f'Ошбика FK: {col_name} - {value_text}')
                        return None

            data[col_name] = value_text

        return data

    def is_error(self, text):
        self.error_label.setText(text)

    def validate_data(self, row_data):
        columns_info = self.db.get_table_columns(self.table_name)
        validated_data = row_data.copy()

        for col in columns_info:
            col_name = col[1]
            col_type = col[2].upper()
            is_nullable = not col[3]
            is_pk = col[5]

            if is_pk:
                continue

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

    def accept(self):
        data = self.get_current_data()
        if data:
            is_valid, validate_data = self.validate_data(data)

            if is_valid:
                self.result_data = validate_data
                self.error_label.clear()

                super().accept()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    ui = Ui_Dialog()

    ui.show()
    sys.exit(app.exec_())
