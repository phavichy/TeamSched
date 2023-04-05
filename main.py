import sys
import pandas as pd
import process_main as pp
from PyQt6.QtWidgets import (QApplication,
                             QLabel,
                             QWidget,
                             QComboBox,
                             QListWidget,
                             QPushButton,
                             QFileDialog,
                             QMainWindow,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QGroupBox,
                             )
import openpyxl


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.browse_button = None
        self.status_bar = None
        self.file_list = None
        self.selector = None
        self.Go_button = None
        self.Export_button = None
        self.initUI()
        self.pdf_files = []
        self.df_all = pd.DataFrame()
        self.df_dep = pd.DataFrame()
        self.midnight_flt = []
        self.df_passive = pd.DataFrame()
        self.df_date = pd.DataFrame()
        self.df_vertical = pd.DataFrame()
        self.df_final = pd.DataFrame()
        self.df_final_block = pd.DataFrame()

    def initUI(self):
        # Widgets
        self.browse_button = QPushButton("Browse", self)
        self.status_bar = QLabel("Status", self)
        self.file_list = QListWidget(self)
        self.selector = QComboBox(self)
        self.selector.addItems(["Show Original Sched",
                                "Show Flights This Month",
                                "Show Flights After Midnight",
                                "Show Flights with Passive Pilots",
                                "Show Summary Sched sort by Date",
                                "Show Flights Sorts in Vertical List",
                                "Show Flight in Team Sched Format with Block",
                                "Show Flight in Team Sched Format w/o Block"
                                ])
        self.Go_button = QPushButton("Show", self)
        self.Export_button = QPushButton("Export All to .xlsx", self)
        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.status_bar)
        layout.addWidget(self.file_list)
        layout.addWidget(self.selector)
        layout.addWidget(self.Go_button)
        layout.addWidget(self.Export_button)
        self.setLayout(layout)
        # Connect Signals & Slots
        self.browse_button.clicked.connect(self.pdf_process)
        self.Go_button.clicked.connect(self.go_activate)
        self.Export_button.clicked.connect(self.export_xlsx)
        # Set window properties
        self.setGeometry(200, 200, 600, 900)
        self.setWindowTitle("Sched Team PDF Analyzer")
        self.show()

    def pdf_process(self):
        self.file_list.addItems(["Selecting PDF Files", "---------------------"])
        self.pdf_files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if len(self.pdf_files) == 0:
            self.file_list.addItem("No PDFs Selected")
            return
        self.file_list.addItems(self.pdf_files)
        self.df_all, self.df_dep, self.midnight_flt, self.df_passive, self.df_date, self.df_vertical, self.df_final, \
            self.df_final_block = pp.sched_process(self.pdf_files)
        self.file_list.addItem("PDFs Processed, Ready")

    def go_activate(self):
        # Show the selected pdf files
        if self.selector.currentText() == "Show Original Sched":
            print(self.df_all.to_string())
            self.file_list.addItems(["Showing Original Sched", "---------------------"])
        elif self.selector.currentText() == "Show Flights This Month":
            print(self.df_dep)
            self.file_list.addItems(["Showing List of Flights This Month", "---------------------"])
        elif self.selector.currentText() == "Show Flights After Midnight":
            print(self.midnight_flt)
            self.file_list.addItems(["Showing Flights Depart after Midnight", "---------------------"])
        elif self.selector.currentText() == "Show Flights with Passive Pilots":
            print(self.df_passive.to_string())
            self.file_list.addItems(["Showing Flights with Passive Pilots", "---------------------"])
        elif self.selector.currentText() == "Show Summary Sched sort by Date":
            print(self.df_date.to_string())
            self.file_list.addItems(["Showing Sched sort by Date", "---------------------"])
        elif self.selector.currentText() == "Show Flights Sorts in Vertical List":
            print(self.df_vertical.to_string())
            self.file_list.addItems(["Showing Flights Sorts in Vertical List", "---------------------"])
        elif self.selector.currentText() == "Show Flight in Team Sched Format with Block":
            self.file_list.addItems(["Showing Flight in Team Sched Format with Block", "---------------------"])
            print(self.df_final_block.to_string())
        elif self.selector.currentText() == "Show Flight in Team Sched Format w/o Block":
            self.file_list.addItems(["Showing Flight in Team Sched Format w/o Block", "---------------------"])
            print(self.df_final.to_string())
        else:
            print("Error: No selection made")

    def export_xlsx(self):
        with pd.ExcelWriter('All APR.xlsx') as writer:
            self.df_all.to_excel(writer, sheet_name='Original Sched')
            self.df_dep.to_excel(writer, sheet_name='DEP Flights list')
            self.df_passive.to_excel(writer, sheet_name='Flight with Passive')
            self.df_date.to_excel(writer, sheet_name='Flight by Date')
            self.df_vertical.to_excel(writer, sheet_name='Vertical Format')
            self.df_final_block.to_excel(writer, sheet_name='SCHED TEAM ONLY with Block')
            self.df_final.to_excel(writer, sheet_name='SCHED TEAM ONLY no Block')
        self.file_list.addItems(["Exported All to .xlsx", "---------------------"])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec())
