import cv2

from PyQt5 import QtCore
from PyQt5 import QtGui


class IService(QtCore.QThread):
    def __init__(self, camera, parent=None):
        super(IService, self).__init__(parent)
        self.camera = camera
        self.is_on = True
    
    def run(self):
        pass

    @QtCore.pyqtSlot(bool)
    def on(self, is_on):
        self.is_on = is_on