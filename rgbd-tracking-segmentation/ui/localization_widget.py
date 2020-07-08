from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.image_viewer import ImageViewer


class LocalizationWidget(QDockWidget):
    def __init__(self, parent=None):
        super(LocalizationWidget, self).__init__(parent)

        self.tracking_viewer = ImageViewer(640, 480)
        self.debug_viewer_1 = ImageViewer()
        self.debug_viewer_2 = ImageViewer()
        self.tracking_button = QPushButton('Tracking')
        self.tracking_button.setCheckable(True)
        self.tracking_button.setChecked(True)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.debug_viewer_1, 0, 0)
        grid_layout.addWidget(self.debug_viewer_2, 0, 1)
        grid_layout.addWidget(self.tracking_viewer, 1, 0, 1, 2)
        
        status_bar = QStatusBar()
        status_bar.addWidget(self.setStatusLabel("cat is on the table"))
        
        tracking_layout = QVBoxLayout()
        tracking_layout.addLayout(grid_layout)
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

    def getImageSignal(self):
        return self.tracking_viewer.setImage

    def getDebugSignal(self):
        return self.debug_viewer_1.setImage, self.debug_viewer_2.setImage

    def isOn(self):
        return self.tracking_button.isChecked()