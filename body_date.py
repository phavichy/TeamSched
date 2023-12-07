import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QDateEdit, QPushButton
from PyQt6.QtCore import QDate


class MonthYearSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Month and Year")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a month and year:"))

        self.date_edit = QDateEdit(self)
        self.date_edit.setDisplayFormat("MMM yyyy")
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

    def get_selected_month_and_year(self):
        selected_date = self.date_edit.date()
        return selected_date.year(), selected_date.month()


def select_month_and_year():
    app = QApplication.instance() or QApplication(sys.argv)
    dialog = MonthYearSelectionDialog()
    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:
        return dialog.get_selected_month_and_year()
    else:
        return None, None


def body_date(df_all, df_dep):
    year, month = select_month_and_year()
    if year is None or month is None:
        print("No month and year selected.")
        return
    if month == 12:
        num_days = 31  # December always has 31 days
    else:
        num_days = (datetime(year, month + 1, 1) - timedelta(days=1)).day
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, num_days)

    dates_list = df_all.columns[2:]
    flight_numbers = df_dep['TG'].astype(str).tolist()
    df_date = pd.DataFrame(columns=flight_numbers, index=dates_list)
    df_date = df_date.fillna('')

    pattern = r'\b[a-zA-Z]{1,2}\b'
    for date in dates_list:
        for flight_number in flight_numbers:
            ids = df_all[df_all[date].astype(str).str.contains(flight_number, regex=True)]['ID'].tolist()
            for pilot_id in ids:
                cell_value = df_all.loc[df_all['ID'] == pilot_id, date].iloc[0]
                match = re.search(pattern, cell_value)
                if match:
                    code = match.group(0)
                else:
                    code = ''
                df_date.loc[date, flight_number] += f"{pilot_id}{code} "

    dates = pd.date_range(start_date, end_date, freq='D')
    date_index = pd.DatetimeIndex(dates)
    date_index = [d.strftime('%a%d%b') for d in date_index]

    df_date.rename(index=dict(zip(df_date.index, date_index)), inplace=True)
    return df_date

