import cv2

from PyQt5 import QtCore
from PyQt5 import QtGui

from service import IService
from utils import cv2qimage


class VideoService(IService):
    rgb_signal = QtCore.pyqtSignal(QtGui.QImage)
    depth_signal = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, camera):
        super(VideoService, self).__init__(camera)

    @QtCore.pyqtSlot()
    def run(self):
        try:
            while True:
                color_image, _, depth_image = self.camera.get_frames()

                color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                color_image = cv2.resize(color_image, dsize=(640, 480), interpolation=cv2.INTER_LINEAR)
                height, width, _ = color_image.shape
                qt_rgb_image = QtGui.QImage(color_image.data,
                                        width,
                                        height,
                                        color_image.strides[0],
                                        QtGui.QImage.Format_RGB888)

                                        

                self.rgb_signal.emit(qt_rgb_image)

                depth_image = cv2.cvtColor(depth_image, cv2.COLOR_BGR2RGB)
                depth_image = cv2.resize(depth_image, dsize=(640, 480), interpolation=cv2.INTER_LINEAR)
                height, width, _ = depth_image.shape
                qt_depth_image = QtGui.QImage(depth_image.data,
                                        width,
                                        height,
                                        depth_image.strides[0],
                                        QtGui.QImage.Format_RGB888)

                self.depth_signal.emit(qt_depth_image)

                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(1, loop.quit)
                loop.exec_()
        finally:
            self.camera.stop()

    @QtCore.pyqtSlot()
    def stop(self):
        self.camera.stop()
    