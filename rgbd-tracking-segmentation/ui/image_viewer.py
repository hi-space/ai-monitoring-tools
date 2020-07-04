from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import QtGui


class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.label = QLabel(self)
        self.label.setPixmap(QtGui.QPixmap('tmp.jpg'))
        self.label.resize(640, 480)

        # self.image = QtGui.QImage()
        # self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        pass
        # painter = QtGui.QPainter(self)
        # painter.drawImage(0, 0, self.image)
        # self.image = QtGui.QImage()

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")
        
        # self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        
        self.label.resize(image.size())
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

        # self.update()
