import cv2

from PyQt5 import QtCore
from PyQt5 import QtGui

from tracking.tracking_model import TrackingModel
from config import TrackingConfig

from service import IService


class LocalizationService(IService):
    tracking_signal = QtCore.pyqtSignal(QtGui.QImage)
    debug_signal_1 = QtCore.pyqtSignal(QtGui.QImage)
    debug_signal_2 = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, camera, segmentation):
        super(LocalizationService, self).__init__(camera)
        self.model = TrackingModel(config_detection = TrackingConfig.config_detection,
                                    config_deepsort = TrackingConfig.config_deepsort,
                                    on_gpu=TrackingConfig.on_gpu)
        self.segmentation = segmentation
    
    def run(self):
        while True:
            try:
                if self.is_on:
                    rgb_frame, _, _ = self.camera.get_frames()

                    seg_result = self.segmentation.getSegResult()

                    tracking_image = self.model.inference(rgb_frame)
                    tracking_image = cv2.cvtColor(tracking_image, cv2.COLOR_BGR2RGB)

                    qt_tracking_image = QtGui.QImage(tracking_image.data, 
                                                    640, 480, 
                                                    tracking_image.strides[0], 
                                                    QtGui.QImage.Format_RGB888)
                    
                    self.tracking_signal.emit(qt_tracking_image)

                    #TODO
                    # debug images

                    qt_debug_image = QtGui.QImage(tracking_image.data,
                                                    640, 480,
                                                    tracking_image.strides[0], 
                                                    QtGui.QImage.Format_RGB888)
                    
                    self.debug_signal_1.emit(qt_debug_image)
                    self.debug_signal_2.emit(qt_debug_image)
            except Exception as e:
                print(e)