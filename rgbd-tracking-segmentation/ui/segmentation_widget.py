from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.image_viewer import ImageViewer
from utils import title_text, description_text


class SegmentationWidget(QDockWidget):
    def __init__(self, parent=None):
        super(SegmentationWidget, self).__init__(parent)

        title_label = title_text("Segmentation")
        
        self.seg_viewer_1 = ImageViewer()
        self.seg_viewer_2 = ImageViewer()
        self.seg_viewer_3 = ImageViewer()
        self.seg_button = QPushButton('Segmentation')
        self.seg_button.setCheckable(True)
        self.seg_button.setChecked(True)

        seg_layout = QVBoxLayout()
        seg_layout.setAlignment(Qt.AlignCenter)
        seg_layout.addWidget(title_label)
        seg_layout.addWidget(self.seg_viewer_1)
        seg_layout.addWidget(description_text("segmentation model 1"))
        
        seg_layout.addWidget(description_text())
        seg_layout.addWidget(self.seg_viewer_2)
        seg_layout.addWidget(description_text("segmentation model 2"))
        seg_layout.addWidget(self.seg_viewer_3)
        seg_layout.addWidget(description_text("segmentation model 3"))
        seg_layout.addWidget(self.seg_button)        
        
        seg_widget = QWidget()
        seg_widget.setLayout(seg_layout)

        # self.setWindowTitle('Segmentation')
        self.seg_button.setFixedHeight(50)

        self.setFixedHeight(1100)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWidget(seg_widget)

    def setButtonEvent(self, event):
        self.seg_button.clicked.connect(event)

    def getImageSignal(self):
        return self.seg_viewer_1.setImage, self.seg_viewer_2.setImage, self.seg_viewer_3.setImage

    def isOn(self):
        return self.seg_button.isChecked()

