import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QListWidget,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
)

app = QApplication([])
window = QWidget()
window.setWindowTitle("PyQt6 App")
window.setGeometry(100, 100, 280, 80)
hellomsg = QLabel("<h1>Hello World!</h1>", parent=window)
hellomsg.move(60, 15)

layout = QVBoxLayout()
layout.addWidget(QPushButton("1"))
layout.addWidget(QPushButton("2"))
layout.addWidget(QPushButton("3"))
window.setLayout(layout)


window.show()
sys.exit(app.exec())
