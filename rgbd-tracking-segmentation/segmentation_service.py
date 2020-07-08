import cv2

from PyQt5 import QtCore
from PyQt5 import QtGui

from segmentation.convert_my_data import reshape_nyu_rgb, reshape_sun_depth
from segmentation.color_mapping import *
from segmentation.segmentation_model import SegmentationModel
from segmentation.npy_to_image import segmentation_overlay
from config import SegConfig

from service import IService


class SegmentationService(IService):
    seg_signal_1 = QtCore.pyqtSignal(QtGui.QImage)
    seg_signal_2 = QtCore.pyqtSignal(QtGui.QImage)
    seg_signal_3 = QtCore.pyqtSignal(QtGui.QImage)
    seg_signal_4 = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, camera):
        super(SegmentationService, self).__init__(camera)
        self.seg_result = None

    def run(self):
        try:
            if self.is_on:
                rgb_frame, depth_frame, _ = self.camera.get_frames()

                rgb_data = reshape_nyu_rgb(rgb_frame)
                depth_data = reshape_sun_depth(depth_frame)

                model_list = [SegConfig.SUN_RGB_SCENENET_PRETRAIN, SegConfig.SUN_RGBD_SCENENET_PRETRAIN,
                                SegConfig.SUN_RGB_SCENENET_PRETRAIN, SegConfig.SUN_RGBD_SCENENET_PRETRAIN]
                
                _, qt_seg_image = self.getInference(SegmentationModel(model_list[0], SegConfig.on_gpu, SegConfig.eval_mode),
                                                                        rgb_frame, rgb_data, depth_data)
                self.seg_signal_1.emit(qt_seg_image)
                self.seg_signal_3.emit(qt_seg_image)

                self.seg_result, qt_seg_image = self.getInference(SegmentationModel(model_list[1], SegConfig.on_gpu, SegConfig.eval_mode),
                                                                        rgb_frame, rgb_data, depth_data)
                self.seg_signal_2.emit(qt_seg_image)
                self.seg_signal_4.emit(qt_seg_image)
        except Exception as e:
            print(e)

    def getInference(self, model, rgb_frame, rgb_data, depth_data):
        result = model.inference(rgb_data, depth_data)
        seg_overlay = segmentation_overlay(rgb_frame, result, 0.5)
        seg_overlay = cv2.cvtColor(seg_overlay, cv2.COLOR_BGR2RGB)
        qt_seg_image = QtGui.QImage(seg_overlay.data, 640, 480, seg_overlay.strides[0], QtGui.QImage.Format_RGB888)
        return result, qt_seg_image

    def getSegResult(self):
        return self.seg_result
