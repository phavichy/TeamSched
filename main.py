import sys
import pandas as pd
import process as pp
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget, QComboBox,
                             QListWidget, QPushButton, QFileDialog, QMainWindow,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,

                             )


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.pdf_files = []
        self.df_all = pd.DataFrame()
        self.df_flt_dep_only = pd.DataFrame()
        self.midnight_flt = pd.DataFrame()
        self.df_passive = pd.DataFrame()
        self.df_date = pd.DataFrame()
        self.df_pilots_all = pd.DataFrame()
        self.df_final = pd.DataFrame()

    def initUI(self):
        # Widgets
        self.browse_button = QPushButton("Browse", self)
        self.status_bar = QLabel("Status", self)
        self.file_list = QListWidget(self)
        self.selector = QComboBox(self)
        self.selector.addItems(["Show Original Sched", "Show Flights This Month", "Show Flights After Midnight"
                                , "Show Flights with Passive Pilots", "Show Summary Sched sort by Date"
                                , "Show Flights Sorts in Vertical List", "Export Flight in CSV Format"])
        self.Go_button = QPushButton("Go", self)

        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.status_bar)
        layout.addWidget(self.file_list)
        layout.addWidget(self.selector)
        layout.addWidget(self.Go_button)
        self.setLayout(layout)
        # Connect Signals & Slots
        self.browse_button.clicked.connect(self.pdf_process)
        self.Go_button.clicked.connect(self.go_activate)
        # Set window properties
        self.setGeometry(200, 200, 640, 480)
        self.setWindowTitle("Sched Team PDF Analyzer")
        self.show()

    def pdf_process(self):
        self.file_list.addItems(["PDF Files Selected, Please wait."])
        self.file_list.addItems(["Now Analyzing PDFs..."])
        self.pdf_files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        self.file_list.addItems(self.pdf_files)

        # Process the selected pdf files
        self.df_all, self.df_flt_dep_only, self.midnight_flt, self.df_passive, self.df_date, self.df_pilots_all \
            , self.df_final, completed_text = pp.sched_process(self.pdf_files)
        self.file_list.addItem(completed_text)

    def go_activate(self):
        # Show the selected pdf files
        if self.selector.currentText() == "Show Original Sched":
            print(self.df_all.to_string())
            self.file_list.addItems(["Original Sched Showed", "---------------------"])
        elif self.selector.currentText() == "Show Flights This Month":
            print(self.df_flt_dep_only)
            self.file_list.addItems(["Flights This Month Showed", "---------------------"])
        elif self.selector.currentText() == "Show Flights After Midnight":
            print(self.midnight_flt)
            self.file_list.addItems(["Flights After Midnight Showed", "---------------------"])
        elif self.selector.currentText() == "Show Flights with Passive Pilots":
            print(self.df_passive.to_string())
            self.file_list.addItems(["Flights with Passive Pilots Showed", "---------------------"])
        elif self.selector.currentText() == "Show Summary Sched sort by Date":
            print(self.df_date.to_string())
            self.file_list.addItems(["Summary Sched sort by Date Showed", "---------------------"])
        elif self.selector.currentText() == "Show Flights Sorts in Vertical List":
            print(self.df_pilots_all.to_string())
            self.file_list.addItems(["Flights Sorts in Vertical List Showed", "---------------------"])
        elif self.selector.currentText() == "Export Flight in CSV Format":
            self.df_final.to_csv('SCHED.csv', header=False, index=False)
            self.file_list.addItems(["Export Flight in CSV Format Completed", "---------------------"])
        else:
            print("Error: No selection made")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec())
