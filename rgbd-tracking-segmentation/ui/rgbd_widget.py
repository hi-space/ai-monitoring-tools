from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.image_viewer import ImageViewer


class RGBDWidget(QDockWidget):
    def __init__(self, parent=None):
        super(RGBDWidget, self).__init__(parent)

        self.rgb_viewer = ImageViewer()
        self.depth_viewer = ImageViewer()

        rgbd_layout = QHBoxLayout()
        rgbd_layout.addWidget(self.rgb_viewer)
        rgbd_layout.addWidget(self.depth_viewer)

        rgbd_widget = QWidget()
        rgbd_widget.setLayout(rgbd_layout)
        
        self.setWindowTitle('RGBD')
        self.setWidget(rgbd_widget)

    def getImageSignal(self):
        return self.rgb_viewer.setImage, self.depth_viewer.setImage
