from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import QtGui


class ImageViewer(QWidget):
    def __init__(self, w=320, h=240, parent=None):
        super(ImageViewer, self).__init__(parent)

        self.setFixedSize(w, h)

        self.label = QLabel(self)        
        self.label.setPixmap(QtGui.QPixmap('tmp.jpg'))

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")
        
        # if image.size() != self.size():
        #     self.setFixedSize(image.size())

        self.setFixedSize(self.size())
        
        self.label.resize(self.width(), self.height())
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio)

        self.label.setPixmap(pixmap)        
