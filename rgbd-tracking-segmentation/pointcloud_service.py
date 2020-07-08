import cv2

from PyQt5 import QtCore
from PyQt5 import QtGui

from service import IService


class PointCloudService(IService):
    pcd_signal = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, camera):
        super(PointCloudService, self).__init__(camera)

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            try:
                if self.is_on:
                    out = self.camera.get_pointcloud()
                    
                    out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
                    height, width, _ = out.shape

                    qt_pcd_image = QtGui.QImage(out.data,
                                            width,
                                            height,
                                            out.strides[0],
                                            QtGui.QImage.Format_RGB888)

                    self.pcd_signal.emit(qt_pcd_image)
            except:
                pass

