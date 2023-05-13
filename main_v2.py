import sys
import pandas as pd
import body_import as b1
import body_selectflt as b2
import body_passive as b3
import body_date as b4
import body_final as b5
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
        self.midnight_flt = []
        self.df_flt = pd.DataFrame()
        self.df_dep = pd.DataFrame()
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
        self.selector.addItems(["Show df_all",
                                "Show midnight_flt",
                                "Show df_flt",
                                "Show df_dep",
                                "Show df_passive",
                                "Show df_date",
                                "Show df_vertical",
                                "Show df_final",
                                "Show df_final_block"
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
        self.browse_button.clicked.connect(self.process_import)
        self.Go_button.clicked.connect(self.output_print)
        self.Export_button.clicked.connect(self.export_xlsx)
        # Set window properties
        self.setGeometry(200, 200, 600, 600)
        self.setWindowTitle("Sched Team PDF Analyzer")
        self.show()

    def process_import(self):
        self.file_list.addItems(["Selecting PDF Files", "---------------------"])
        self.pdf_files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if len(self.pdf_files) == 0:
            self.file_list.addItem("No PDFs Selected")
            return
        self.file_list.addItems(self.pdf_files)
        self.df_all, self.df_flt, self.midnight_flt = b1.body_import(self.pdf_files)
        self.file_list.addItem("df_all, df_flt ready")
        self.file_list.addItem("Please Select applicable Flight Numbers")
        self.process_select_flights()

    def process_select_flights(self):
        self.df_dep = b2.body_select_flt(self.df_flt)
        if self.df_dep is not None:
            self.file_list.addItem("df_dep ready")
        else:
            self.file_list.addItem("No flights selected")
        self.process_passive()

    def process_passive(self):
        self.df_passive = b3.body_passive(self.df_all)
        self.file_list.addItem("df_passive ready")
        self.process_date()

    def process_date(self):
        self.df_date = b4.body_date(self.df_all, self.df_dep)
        self.file_list.addItem("df_date ready")
        self.process_final()

    def process_final(self):
        self.df_vertical, self.df_final, self.df_final_block = b5.body_final(self.df_date)
        self.file_list.addItem("df_vertical, df_final and df_final_block ready")

    def output_print(self):
        # Show the selected pdf files
        if self.selector.currentText() == "Show df_all":
            print(self.df_all.to_string())
            self.file_list.addItems(["Show df_all", "---------------------"])
        elif self.selector.currentText() == "Show midnight_flt":
            print(self.midnight_flt)
            self.file_list.addItems(["Show midnight_flt", "---------------------"])
        elif self.selector.currentText() == "Show df_flt":
            print(self.df_flt.to_string())
            self.file_list.addItems(["Show df_flt", "---------------------"])
        elif self.selector.currentText() == "Show df_dep":
            print(self.df_dep.to_string())
            self.file_list.addItems(["Show df_dep", "---------------------"])
        elif self.selector.currentText() == "Show df_passive":
            print(self.df_passive.to_string())
            self.file_list.addItems(["Show df_passive", "---------------------"])
        elif self.selector.currentText() == "Show df_date":
            print(self.df_date.to_string())
            self.file_list.addItems(["Show df_date", "---------------------"])
        elif self.selector.currentText() == "Show df_vertical":
            print(self.df_vertical.to_string())
            self.file_list.addItems(["Show df_vertical", "---------------------"])
        elif self.selector.currentText() == "Show df_final":
            print(self.df_final.to_string())
            self.file_list.addItems(["Show df_final", "---------------------"])
        elif self.selector.currentText() == "Show df_final_block":
            print(self.df_final_block.to_string())
            self.file_list.addItems(["Show df_final_block", "---------------------"])
        else:
            print("Error: No selection made")

    def export_xlsx(self):
        file_path, _ = QFileDialog.getSaveFileName(None, "Save As", "", "Excel files (*.xlsx);;All Files (*)")

        if file_path:
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            with pd.ExcelWriter(file_path) as writer:
                self.df_all.to_excel(writer, sheet_name='All')
                self.df_flt.to_excel(writer, sheet_name='Flt')
                self.df_dep.to_excel(writer, sheet_name='Dep')
                self.df_passive.to_excel(writer, sheet_name='Passive')
                self.df_date.to_excel(writer, sheet_name='Date')
                self.df_vertical.to_excel(writer, sheet_name='Vertical')
                self.df_final.to_excel(writer, sheet_name='Final')
                self.df_final_block.to_excel(writer, sheet_name='Final Block')
            self.file_list.addItems(["Exported All to .xlsx", "---------------------"])
        else:
            self.file_list.addItems(["Exporting All canceled", "---------------------"])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec())
