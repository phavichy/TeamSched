import sys
import pandas as pd
import pdf_processing as pp
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget,
    QListWidget, QPushButton, QFileDialog, QMainWindow,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox)

class WelcomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Welcome to Sched Analyzer')
        self.setGeometry(100, 100, 640, 480)
        self.initUI()

    def initUI(self):
        # create a

    def upload_pdf(self):
        self.pdf_files = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        self.file_list.addItems(self.pdf_files)
        df_all, midnight_flt, df_flt_dep_only, df_passive, df_date, df_pilots_all, df_final = pp.process_pdfs(
            self.pdf_files)
        print(df_final)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wp = WelcomePage()
    sys.exit(app.exec())

# class WelcomePage(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.pdf_files = []
#         self.initui()
#         self.get_pdf_files()
#
#     def initui(self):
#         # Create widgets for browsing data
#         self.browse_button = QPushButton("Browse", self)
#         self.file_list = QListWidget(self)
#         self.show_data_button = QPushButton("Show Data", self)
#         self.addWidget(self.show_data_button)
#         # Set up layout
#         layout = QtWidgets.QVBoxLayout(self)
#         layout.addWidget(self.browse_button)
#         layout.addWidget(self.file_list)
#         self.setLayout(layout)
#         # Connect signals and slots
#         self.browse_button.clicked.connect(self.get_pdf_files)
#         # Set window properties
#         self.setGeometry(300, 500, 640, 480)
#         self.setWindowTitle("Welcome")
#         self.show()
#     def get_pdf_files(self):
#         self.pdf_files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
#         self.file_list.addItems(self.pdf_files)
#         # Process the selected pdf files
#         df_all, midnight_flt, df_flt_dep_only, df_passive, df_date, df_pilots_all, df_final = pp.process_pdfs(self.pdf_files)
#         print(df_final.to_string())