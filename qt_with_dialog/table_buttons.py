from PyQt5 import QtCore, QtGui, QtWidgets
import db


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, db):
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
        table_names = db.get_name_of_tables()

        for name in table_names:
            pushButton = QtWidgets.QPushButton(self.centralwidget)
            pushButton.setStyleSheet('font-size: 20px;')
            pushButton.setObjectName(f'pushButton_{name}')
            pushButton.setText(name)

            self.verticalLayout.addWidget(pushButton)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    db = db.DB('warehouse.db')

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, db)
    MainWindow.show()
    sys.exit(app.exec_())
