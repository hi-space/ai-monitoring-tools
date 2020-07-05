from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.image_viewer import ImageViewer


class PointCloudWidget(QDockWidget):
    def __init__(self, parent=None):
        super(PointCloudWidget, self).__init__(parent)

        self.pcd_viewer = ImageViewer()
        self.pcd_button = QPushButton('PointCloud')

        pcd_layout = QVBoxLayout()
        pcd_layout.addWidget(self.pcd_viewer)
        pcd_layout.addWidget(self.pcd_button)

        pcd_widget = QWidget()
        pcd_widget.setLayout(pcd_layout)

        self.setWindowTitle('PointCloud')
        self.setWidget(pcd_widget)

    def setButtonEvent(self, event):
        self.pcd_button.clicked.connect(event)

    def setMouseEvent(self, func):
        self.pcd_viewer.mouseMoveEvent = func

    def getImageSignal(self):
        return self.pcd_viewer.setImage