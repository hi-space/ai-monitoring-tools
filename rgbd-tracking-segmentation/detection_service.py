import cv2
import time

from PyQt5 import QtCore
from PyQt5 import QtGui

from tracking.tracking_model import TrackingModel
from tracking import bbox_utils, det_utils
from tracking.utils.draw import draw_boxes
from algorithms.localization import Localization
from config import TrackingConfig

from service import IService
from publisher import RedisPublisher

from debug.tracer import pdb_pm

class DetectionService(IService):
    tracking_signal = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, camera, segmentation):
        super(DetectionService, self).__init__(camera)
        self.model = TrackingModel(config_detection = TrackingConfig.config_detection,
                                    config_deepsort = TrackingConfig.config_deepsort,
                                    on_gpu=TrackingConfig.on_gpu)

        self.segmentation = segmentation

    @pdb_pm
    def run(self):
        reference_frame_is_set = False
        while True:
            if self.is_on:
                ret, self.rgb_frame, self.raw_depth_frame, cm_depth_frame = self.camera.get_frames()
                if ret == False:
                    continue

                if not self.segmentation.isRunning():
                    if not reference_frame_is_set:
                        self.reference_depth_frame = self.raw_depth_frame
                        reference_frame_is_set = True
                else:
                    if reference_frame_is_set:
                        reference_frame_is_set = False

                    self.cm_depth_frame = cm_depth_frame

                # cv2.imwrite('./data2/beammice-rgb-%s.jpg' % str(time.time()), self.rgb_frame)

                self.detection_outputs = self.model.inference(self.rgb_frame)

                tracking_image = cv2.cvtColor(self.rgb_frame, cv2.COLOR_BGR2RGB)

                if self.detection_outputs is not None:
                    bbox_xywh, _, cls_ids, _ = det_utils.get_masked_det_outputs(self.detection_outputs, det_utils.get_custom_mask)
                    det_bbox_xyxy = bbox_utils.xyxy_to_xywh(bbox_xywh, deepcopy=True)
                    tracking_image = draw_boxes(tracking_image, det_bbox_xyxy, cls_ids, class_names='beammice')

                qt_tracking_image = QtGui.QImage(tracking_image.data, 
                                                640, 480, 
                                                tracking_image.strides[0], 
                                                QtGui.QImage.Format_RGB888)
                
                self.tracking_signal.emit(qt_tracking_image)


    def getDetResult(self):
        if hasattr(self, 'detection_outputs'):
            return self.detection_outputs
        else:
            return None

        
    def getDetFrames(self):
        if hasattr(self, 'rgb_frame') and hasattr(self, 'raw_depth_frame') and hasattr(self, 'cm_depth_frame'):
            if self.segmentation.isRunning():
                return (self.rgb_frame, self.raw_depth_frame, self.cm_depth_frame, self.raw_depth_frame)
            else:
                if hasattr(self, 'reference_depth_frame'):
                    return (self.rgb_frame, self.raw_depth_frame, self.cm_depth_frame, self.reference_depth_frame)
                else:
                    return (self.rgb_frame, self.raw_depth_frame, self.cm_depth_frame, self.raw_depth_frame)

        else:
            return None, None, None, None