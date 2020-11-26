import cv2

from PyQt5 import QtCore
from PyQt5 import QtGui

from segmentation.convert_my_data import reshape_nyu_rgb, reshape_sun_depth
from segmentation.color_mapping import *
from segmentation.segmentation_model import SegmentationModel
from segmentation.npy_to_image import segmentation_overlay
from config import SegConfig

from service import IService

from debug.tracer import pdb_pm

import threading

class SegmentationService(IService):
    seg_signal_1 = QtCore.pyqtSignal(QtGui.QImage)
    seg_signal_2 = QtCore.pyqtSignal(QtGui.QImage)
    seg_signal_3 = QtCore.pyqtSignal(QtGui.QImage)

    seg_model_1 = SegmentationModel(SegConfig.SUN_RGB_SCENENET_PRETRAIN, SegConfig.on_gpu, SegConfig.eval_mode)
    seg_model_2 = SegmentationModel(SegConfig.SUN_RGB_IMAGENET_PRETRAIN, SegConfig.on_gpu, SegConfig.eval_mode)
    seg_model_3 = SegmentationModel(SegConfig.SUN_RGB_NO_PRETRAIN, SegConfig.on_gpu, SegConfig.eval_mode)

    def __init__(self, camera):
        super(SegmentationService, self).__init__(camera)
        self.seg_result = None
        self.cv = threading.Condition()

    @pdb_pm
    def run(self):
        while True:
            try:
                if self.is_on:
                    ret, rgb_frame, depth_frame, _ = self.camera.get_frames()
                    if ret == False or rgb_frame is None or depth_frame is None:
                        continue

                    rgb_data = reshape_nyu_rgb(rgb_frame)
                    depth_data = reshape_sun_depth(depth_frame)
                    
                    self.seg_result, qt_seg_image_1 = self.getInference(self.seg_model_1, rgb_frame, rgb_data, depth_data)
                    self.seg_signal_1.emit(qt_seg_image_1)

                    _, qt_seg_image_2 = self.getInference(self.seg_model_2, rgb_frame, rgb_data, depth_data)
                    self.seg_signal_2.emit(qt_seg_image_2)

                    _, qt_seg_image_3 = self.getInference(self.seg_model_3, rgb_frame, rgb_data, depth_data)
                    self.seg_signal_3.emit(qt_seg_image_3)
                else:
                    self.cv.acquire()
                    self.cv.wait()
                    self.cv.release()

            except Exception as e:
                print(e)

    def getInference(self, model, rgb_frame, rgb_data, depth_data):
        result = model.inference(rgb_data, depth_data)
        seg_overlay = segmentation_overlay(rgb_frame, result, 0.5)
        seg_overlay = cv2.cvtColor(seg_overlay, cv2.COLOR_BGR2RGB)
        qt_seg_image = QtGui.QImage(seg_overlay.data, 640, 480, seg_overlay.strides[0], QtGui.QImage.Format_RGB888)
        return result, qt_seg_image

    def getSegResult(self, apply_cls_map=False):

        if self.is_on:
            self.cv.acquire()
            try:
                self.cv.notify()
            except:
                pass
            self.cv.release()

        segpred_im = self.seg_result

        if segpred_im is None:
            return None

        if apply_cls_map:
            # import pdb; pdb.set_trace()
            etcs_indices = (segpred_im != 5) & (segpred_im != 3) & (segpred_im != 12) # (floor, ceiling, wall)
            wall_indices = (segpred_im == 8) | (segpred_im == 12) | (segpred_im == 13) # (wall, window, picture)

            segpred_im[etcs_indices] = 40  # apply etc classes 40
            segpred_im[wall_indices] = 20  # apply wall classes 20
            # floor class = 5
            
        return segpred_im

    def isRunning(self):
        return self.is_on
