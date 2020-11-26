from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.image_viewer import ImageViewer
from utils import title_text


class RGBDWidget(QDockWidget):
    def __init__(self, window_title='', parent=None):
        super(RGBDWidget, self).__init__(parent)

        title_label = title_text("RAW Sensor Data")

        self.rgb_viewer = ImageViewer()
        self.depth_viewer = ImageViewer()

        rgbd_layout = QVBoxLayout()
        rgbd_layout.setAlignment(Qt.AlignCenter)
        rgbd_layout.setAlignment(title_label, Qt.AlignTop)
        rgbd_layout.addWidget(title_label)
        rgbd_layout.addWidget(self.rgb_viewer)
        rgbd_layout.addWidget(self.depth_viewer)

        rgbd_widget = QWidget()
        rgbd_widget.setLayout(rgbd_layout)
        
        self.setWindowTitle(window_title)
        self.setFixedHeight(600)
        self.setWidget(rgbd_widget)

    def getImageSignal(self):
        return self.rgb_viewer.setImage, self.depth_viewer.setImage
