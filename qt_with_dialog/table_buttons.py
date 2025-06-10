from PyQt5 import QtCore, QtGui, QtWidgets
import db
import table_info


class Ui_MainWindow(object):
    def __init__(self):
        self.db = None
        self.open_windows = []

    def setupUi(self, MainWindow, db_):
        self.db = db_

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralwidget.setLayout(self.verticalLayout)

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

        self.set_table_name_buttons()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def set_table_name_buttons(self):
        table_names = self.db.get_name_of_tables()

        for name in table_names:
            pushButton = QtWidgets.QPushButton(self.centralwidget)
            pushButton.setStyleSheet('font-size: 20px;')
            pushButton.setObjectName(f'pushButton_{name}')
            pushButton.setText(name)
            pushButton.setProperty('table_name', name)

            self.verticalLayout.addWidget(pushButton)

            pushButton.clicked.connect(lambda checked, current_name=name: self.open_table_info(current_name))

    def open_table_info(self, table_name):
        table_info_window = QtWidgets.QMainWindow()
        ui = table_info.Ui_MainWindow()
        ui.setupUi(table_info_window)

        ui.get_table_info(table_name, self.db)
        self.open_windows.append((table_info_window, ui))

        table_info_window.show()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    db_ = db.DB('warehouse.db')

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, db_)
    MainWindow.show()
    sys.exit(app.exec_())
