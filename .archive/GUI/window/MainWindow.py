import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QSizePolicy, QScrollArea, QStackedWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ChatBubble(QLabel):
    def __init__(self, text, sent_by_user=True):
        super().__init__(text)
        self.sent_by_user = sent_by_user
        self.setWordWrap(True)
        self.setMaximumWidth(360)
        self.setFont(QFont("Segoe UI", 11))
        self.setContentsMargins(20, 14, 20, 14)
        self.setStyleSheet(self.bubble_style())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def bubble_style(self):
        if self.sent_by_user:
            return """
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a67d8, stop:1 #3b49df);
                color: white;
                border-radius: 24px 24px 4px 24px;
                padding: 14px 20px;
                font-weight: 600;
                box-shadow: 0 8px 20px rgba(91, 103, 214, 0.5);
            """
        else:
            return """
                background-color: #2e2b44;
                color: #d0cee9;
                border-radius: 24px 24px 24px 4px;
                padding: 14px 20px;
                font-weight: 500;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            """


class StartPage(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c224f, stop:1 #4e3b7f);
                color: #c8c9ff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QLabel#title {
                font-size: 48px;
                font-weight: 900;
                letter-spacing: 0.05em;
                margin-bottom: 24px;
            }
            QPushButton#startButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a67d8, stop:1 #3b49df);
                border-radius: 32px;
                color: white;
                font-weight: 800;
                font-size: 26px;
                padding: 18px 64px;
                cursor: pointer;
                box-shadow: 0 12px 28px rgba(91, 103, 214, 0.8);
                transition: all 0.3s ease;
            }
            QPushButton#startButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b49df, stop:1 #5a67d8);
                box-shadow: 0 16px 36px rgba(91, 103, 214, 1);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(80, 140, 80, 140)
        layout.setSpacing(40)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Royal Chat & File Sender")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        start_btn = QPushButton("Start Chat")
        start_btn.setObjectName("startButton")
        start_btn.clicked.connect(self.switch_callback)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)


class ModernChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.load_stylesheet())
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header Title
        title = QLabel("Royal Chat & File Sender")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #c8c9ff; letter-spacing: 0.05em;")
        main_layout.addWidget(title)

        # Scrollable chat area container
        self.chat_area = QVBoxLayout()
        self.chat_area.setAlignment(Qt.AlignTop)
        self.chat_area.setSpacing(14)

        scroll_content = QWidget()
        scroll_content.setLayout(self.chat_area)
        scroll_content.setStyleSheet("background: transparent;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #231e45;
                border-radius: 24px;
            }
            QScrollBar:vertical {
                background: #231e45;
                width: 12px;
                margin: 16px 0 16px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #5a67d8;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7f7ff9;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0;
            }
            QScrollBar::add-page, QScrollBar::sub-page {
                background: none;
            }
        """)
        main_layout.addWidget(scroll)

        # Input and send button row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(16)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMinimumHeight(48)
        self.message_input.setObjectName("messageInput")
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.setMinimumWidth(140)
        self.send_button.setMinimumHeight(48)
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self.add_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        # Send file button full width
        self.file_button = QPushButton("📁 Send File")
        self.file_button.setMinimumHeight(52)
        self.file_button.setObjectName("fileButton")
        main_layout.addWidget(self.file_button)

        self.setLayout(main_layout)

    def add_message(self):
        text = self.message_input.text().strip()
        if not text:
            return
        bubble = ChatBubble(text, sent_by_user=True)
        self.chat_area.addWidget(bubble, alignment=Qt.AlignRight)
        self.message_input.clear()

    def load_stylesheet(self):
        return """
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2c224f, stop:1 #4e3b7f);
            color: #c8c9ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 15px;
        }
        QLineEdit#messageInput {
            background: #3b3460;
            border: none;
            border-radius: 24px;
            padding: 0 24px;
            color: #c8c9ff;
            font-size: 16px;
            font-weight: 600;
            selection-background-color: #5a67d8;
            transition: background-color 0.3s ease;
        }
        QLineEdit#messageInput:focus {
            background: #5a67d8;
            color: white;
        }

        QPushButton#sendButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #5a67d8, stop:1 #3b49df);
            border-radius: 24px;
            color: white;
            font-weight: 800;
            font-size: 18px;
            padding: 14px 40px;
            cursor: pointer;
            box-shadow: 0 12px 28px rgba(91, 103, 214, 0.8);
            transition: all 0.3s ease;
        }
        QPushButton#sendButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b49df, stop:1 #5a67d8);
            box-shadow: 0 16px 36px rgba(91, 103, 214, 1);
        }

        QPushButton#fileButton {
            background: #433d70;
            border-radius: 28px;
            color: #c8c9ff;
            font-weight: 700;
            font-size: 20px;
            padding: 18px;
            cursor: pointer;
            box-shadow: 0 12px 30px rgba(67, 61, 112, 0.9);
            transition: background-color 0.3s ease;
        }
        QPushButton#fileButton:hover {
            background: #5a67d8;
            box-shadow: 0 16px 36px rgba(91, 103, 214, 1);
        }
        """


class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Royal Chat & File Sender")
        self.setGeometry(100, 100, 720, 650)
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c224f, stop:1 #4e3b7f);")

        self.start_page = StartPage(self.switch_to_chat)
        self.chat_page = ModernChatApp()

        self.addWidget(self.start_page)
        self.addWidget(self.chat_page)

        self.setCurrentWidget(self.start_page)

    def switch_to_chat(self):
        self.setCurrentWidget(self.chat_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
