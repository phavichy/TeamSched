import sys
import pandas as pd
import pdf_processing as pp
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget,
    QListWidget, QPushButton, QFileDialog, QMainWindow,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox)




class WelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_files = []
        self.initui()
        self.get_pdf_files()

    def initui(self):
        # Create widgets
        self.browse_button = QPushButton("Browse", self)
        self.file_list = QListWidget(self)

        # Set up layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.file_list)
        self.setLayout(layout)

        # Connect signals and slots
        self.browse_button.clicked.connect(self.get_pdf_files)

        # Set window properties
        self.setGeometry(300, 500, 1000, 150)
        self.setWindowTitle("Welcome")
        self.show()
    def get_pdf_files(self):
        self.pdf_files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        self.file_list.addItems(self.pdf_files)
        # Process the selected pdf files
        df = pp.process_pdfs(self.pdf_files)
        print(df)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wp = WelcomePage()
    sys.exit(app.exec())