import pandas as pd
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QListWidget,
                             QDialogButtonBox, QLabel)


def body_select_flt(df_flt):
    dialog = FlightSelectionDialog(df_flt)
    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:
        df_dep = dialog.get_selected_flights()
        df_dep.reset_index(drop=True, inplace=True)
        df_dep.index += 1
        return df_dep
    else:
        return pd.DataFrame()


class FlightSelectionDialog(QDialog):
    def __init__(self, df_flt):
        super().__init__()
        self.df_flt = df_flt
        self.setWindowTitle("Select Flights")
        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.list_widget.setMinimumHeight(800)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select flights from the list:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.button_box)

        for index, row in df_flt.iterrows():
            self.list_widget.addItem(f"Flight {row['TG']}")

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.resize(400, 800)

    def get_selected_flights(self):
        selected_items = self.list_widget.selectedItems()
        selected_indices = [self.list_widget.row(item) for item in selected_items]
        return self.df_flt.iloc[selected_indices]