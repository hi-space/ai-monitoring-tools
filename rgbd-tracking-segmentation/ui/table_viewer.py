from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

from utils import get_current_time


class TableViewer(QWidget):
    def __init__(self, parent=None):
        super(TableViewer, self).__init__(parent)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["time", "status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def addItem(self, status: str):
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(get_current_time()))
        self.table.setItem(0, 1, QTableWidgetItem(status))

    def clear(self):
        self.table.clearContents()
        self.table.setRowCount(0)
