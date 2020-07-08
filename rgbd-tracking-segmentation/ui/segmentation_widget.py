from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.image_viewer import ImageViewer


class SegmentationWidget(QDockWidget):
    def __init__(self, parent=None):
        super(SegmentationWidget, self).__init__(parent)
        
        self.seg_viewer_1 = ImageViewer()
        self.seg_viewer_2 = ImageViewer()
        self.seg_viewer_3 = ImageViewer()
        self.seg_viewer_4 = ImageViewer()
        self.seg_button = QPushButton('Segmentation')
        # self.seg_button.setCheckable(True)
        # self.seg_button.setChecked(True)
        
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.seg_viewer_1, 0, 0)
        grid_layout.addWidget(self.seg_viewer_2, 0, 1)
        grid_layout.addWidget(self.seg_viewer_3, 1, 0)
        grid_layout.addWidget(self.seg_viewer_4, 1, 1)

        seg_layout = QVBoxLayout()
        seg_layout.addLayout(grid_layout)
        seg_layout.addWidget(self.seg_button)
        
        seg_widget = QWidget()
        seg_widget.setLayout(seg_layout)

        self.setWindowTitle('Segmentation')
        self.setWidget(seg_widget)

    def setButtonEvent(self, event):
        self.seg_button.clicked.connect(event)

    def getImageSignal(self):
        return self.seg_viewer_1.setImage, self.seg_viewer_2.setImage, self.seg_viewer_3.setImage, self.seg_viewer_4.setImage
        # return self.seg_viewer_1.setImage, self.seg_viewer_2.setImage

    def isOn(self):
        return self.seg_button.isChecked()