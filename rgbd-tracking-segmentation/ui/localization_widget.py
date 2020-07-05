from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class LocalizationWidget(QDockWidget):
    def __init__(self, tracking_viewer, parent=None):
        super(LocalizationWidget, self).__init__(parent)

        self.tracking_button = QPushButton('Tracking')

        status_bar = QStatusBar()
        status_bar.addWidget(self.setStatusLabel("cat is on the table"))
        
        tracking_layout = QVBoxLayout()
        tracking_layout.addWidget(tracking_viewer)
        tracking_layout.addWidget(status_bar)
        tracking_layout.addWidget(self.tracking_button)
        
        tracking_widget = QWidget()
        tracking_widget.setLayout(tracking_layout)

        self.setWindowTitle('Tracking')
        self.setWidget(tracking_widget)
    
    def setStatusLabel(self, text):
        status_label = QLabel(text)
        status_label.setFixedSize(640, 100)
        status_label.setStyleSheet("color: white;")
        status_label.setFont(QFont('Arial', 15))
        status_label.setAlignment(Qt.AlignCenter)
        return status_label

    def setButtonEvent(self, event):
        self.tracking_button.clicked.connect(event)