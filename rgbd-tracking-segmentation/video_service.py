import cv2

from PyQt5 import QtCore
from PyQt5 import QtGui


class VideoService(QtCore.QObject):
    rgb_signal = QtCore.pyqtSignal(QtGui.QImage)
    depth_signal = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, camera, parent=None):
        super(VideoService, self).__init__(parent)
        self.camera = camera

    @QtCore.pyqtSlot()
    def start(self):
        try:
            while True:
                color_image, _, depth_image = self.camera.get_frames()
                
                w, h = 640, 480

                self.updateImage(color_image, self.rgb_signal, w, h)
                self.updateImage(depth_image, self.depth_signal, w, h)

                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(1, loop.quit)
                loop.exec_()
        finally:
            self.camera.stop()

    def updateImage(self, image, signal, w=640, h=480):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, dsize=(w, h), interpolation=cv2.INTER_LINEAR)
        height, width, _ = image.shape
        qt_image = QtGui.QImage(image.data,
                                width,
                                height,
                                image.strides[0],
                                QtGui.QImage.Format_RGB888)

        signal.emit(qt_image)

    @QtCore.pyqtSlot()
    def stop(self):
        self.camera.stop()
    