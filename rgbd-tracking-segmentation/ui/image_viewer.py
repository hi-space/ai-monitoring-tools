from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ImageViewer(QWidget):
    def __init__(self, w=320, h=240, parent=None):
        super(ImageViewer, self).__init__(parent)

        self.setFixedSize(w, h)

        self.label = QLabel(self)        
        self.label.setPixmap(QPixmap('tmp.jpg'))
        self.label.setAlignment(Qt.AlignCenter)

    @pyqtSlot(QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")
        
        # if image.size() != self.size():
        #     self.setFixedSize(image.size())

        self.setFixedSize(self.size())
        
        self.label.resize(self.width(), self.height())
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)

        self.label.setPixmap(pixmap)        
