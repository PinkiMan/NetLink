from PyQt5 import QtCore, QtGui, QtWidgets
import os

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalFrame = QtWidgets.QFrame(self.centralwidget)
        self.verticalFrame.setGeometry(QtCore.QRect(20, 20, 760, 520))
        self.verticalFrame.setObjectName("verticalFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(20)

        # Title label
        self.label = QtWidgets.QLabel(self.verticalFrame)
        self.label.setObjectName("label")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.verticalLayout.addWidget(self.label)

        # Tree view with file system
        self.treeView = QtWidgets.QTreeView(self.verticalFrame)
        self.treeView.setObjectName("treeView")
        self.treeView.setMinimumHeight(180)
        self.verticalLayout.addWidget(self.treeView)

        # QFileSystemModel setup
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(QtCore.QDir.rootPath())
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(QtCore.QDir.homePath()))
        self.treeView.setHeaderHidden(True)

        # List view for messages
        self.listView = QtWidgets.QListView(self.verticalFrame)
        self.listView.setObjectName("listView")
        self.listView.setMinimumHeight(100)
        self.verticalLayout.addWidget(self.listView)

        # Input and buttons
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.pushButton_Add_FIle = QtWidgets.QPushButton(self.verticalFrame)
        self.pushButton_Add_FIle.setObjectName("pushButton_Add_FIle")
        self.horizontalLayout.addWidget(self.pushButton_Add_FIle)

        self.lineEdit_Input = QtWidgets.QLineEdit(self.verticalFrame)
        self.lineEdit_Input.setObjectName("lineEdit_Input")
        self.horizontalLayout.addWidget(self.lineEdit_Input)

        self.pushButton_Send = QtWidgets.QPushButton(self.verticalFrame)
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.horizontalLayout.addWidget(self.pushButton_Send)

        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Logic
        self.messages = []
        self.pushButton_Send.clicked.connect(self.pressed_send)
        self.pushButton_Add_FIle.clicked.connect(self.pressed_add_file)

        # 🌑 Modern Dark Style
        MainWindow.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }

            QFrame {
                background-color: rgba(40, 40, 60, 0.6);
                border-radius: 20px;
            }

            QLabel {
                color: #ffffff;
            }

            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #3a8ddb, stop:1 #1a73e8);
                border: none;
                color: white;
                padding: 10px 18px;
                border-radius: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #5393ff;
            }

            QLineEdit {
                background-color: #2a2a40;
                border: 1px solid #3a3a5c;
                border-radius: 10px;
                padding: 10px;
                color: #ffffff;
            }

            QListView, QTreeView {
                background-color: #2a2a40;
                border: 1px solid #3a3a5c;
                border-radius: 10px;
            }

            /* Modern Scrollbar Styling */
            QScrollBar:vertical {
                background: #1e1e2f;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #4b6cb7;
                min-height: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #5b7fe0;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                background: #1e1e2f;
                height: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #4b6cb7;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #5b7fe0;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

    def pressed_send(self):
        line = self.lineEdit_Input.text()
        if line.strip():
            self.messages.append(line)
            self.list_model = QtCore.QStringListModel()
            self.listView.setModel(self.list_model)
            self.list_model.setStringList(self.messages)
            self.lineEdit_Input.clear()

    def pressed_add_file(self):
        print('pressed add_file')

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "🚀 Modern Client Panel"))
        self.label.setText(_translate("MainWindow", "Client Name"))
        self.pushButton_Add_FIle.setText(_translate("MainWindow", "📁 Add File"))
        self.pushButton_Send.setText(_translate("MainWindow", "📤 Send"))
        self.pushButton_Send.setShortcut(_translate("MainWindow", "Return"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
