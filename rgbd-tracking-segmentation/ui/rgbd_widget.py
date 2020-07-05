from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class RGBDWidget(QDockWidget):
    def __init__(self, rgb_viewer, depth_viewer, parent=None):
        super(RGBDWidget, self).__init__(parent)

        rgbd_layout = QHBoxLayout()
        rgbd_layout.addWidget(rgb_viewer)
        rgbd_layout.addWidget(depth_viewer)

        rgbd_widget = QWidget()
        rgbd_widget.setLayout(rgbd_layout)
        
        self.setWindowTitle('RGBD')
        self.setWidget(rgbd_widget)

    