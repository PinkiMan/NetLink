import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt

class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Nastavení bezrámečkového a průhledného okna
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Velikost a pozice
        self.setGeometry(100, 100, 400, 300)

        # Layout a widgety
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Textový popisek
        label = QLabel("Vítej v průhledném okně!")
        label.setStyleSheet("color: white; font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        # Tlačítko na zavření
        button = QPushButton("Zavřít")
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                color: black;
                border: 1px solid white;
                border-radius: 10px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 180);
            }
        """)
        button.clicked.connect(self.close)

        layout.addWidget(label)
        layout.addWidget(button, alignment=Qt.AlignCenter)

        # Kontejnerové pozadí s průhlednou barvou
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgba(30, 30, 30, 180); border-radius: 15px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec_())
