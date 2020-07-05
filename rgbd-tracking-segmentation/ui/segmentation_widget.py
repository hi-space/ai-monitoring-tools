from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.image_viewer import ImageViewer


class SegmentationWidget(QDockWidget):
    def __init__(self, parent=None):
        super(SegmentationWidget, self).__init__(parent)
        
        self.seg_viewer = ImageViewer()
        self.seg_button = QPushButton('Segmentation')        
        
        seg_layout = QVBoxLayout()
        seg_layout.addWidget(self.seg_viewer)
        seg_layout.addWidget(self.seg_button)
        
        seg_widget = QWidget()
        seg_widget.setLayout(seg_layout)

        self.setWindowTitle('Segmentation')
        self.setWidget(seg_widget)

    def setButtonEvent(self, event):
        self.seg_button.clicked.connect(event)

    def getImageSignal(self):
        return self.seg_viewer.setImage