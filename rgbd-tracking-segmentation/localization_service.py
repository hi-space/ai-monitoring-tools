import cv2
import numpy as np

from PyQt5 import QtCore
from PyQt5 import QtGui

from tracking.tracking_model import TrackingModel
from segmentation.npy_to_image import segmentation_overlay
from algorithms.localization import Localization
from config import TrackingConfig

from service import IService
from publisher import RedisPublisher

from debug.tracer import pdb_pm

class LocalizationService(IService):
    debug_signal_1 = QtCore.pyqtSignal(QtGui.QImage)
    debug_signal_2 = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, args, detection, segmentation, redis_conf=None, widget=None):
        super(LocalizationService, self).__init__(detection)
        self.model = TrackingModel(config_detection = TrackingConfig.config_detection,
                                    config_deepsort = TrackingConfig.config_deepsort,
                                    on_gpu=TrackingConfig.on_gpu)
        self.localization = Localization(args)
        self.detection = detection
        self.segmentation = segmentation
        self.redis_conf = redis_conf
        self.args = args

        if self.redis_conf:
            self.redis_publish_3d_visualizer = RedisPublisher(redis_conf.topic_for_visualizer)

        if widget:
            self.widget = widget

    def publish_to_open3d_visualizer(self, msg):
        if self.redis_conf:
            self.redis_publish_3d_visualizer.redis_send_pyobj(msg)
        else:
            print("Not publishing to visualizer. Redis has not been configured yet.")
    
    @pdb_pm
    def run(self):
        while True:
            if self.is_on:
                rgb_frame, depth_raw, depth_cm, reference_depth_raw = self.detection.getDetFrames()
                if rgb_frame is None:
                    continue

                seg_result = self.segmentation.getSegResult(apply_cls_map=True)
                if seg_result is None: 
                    continue
                
                detection_outputs = self.detection.getDetResult()

                depth_cm = cv2.cvtColor(depth_cm, cv2.COLOR_BGR2RGB)
                
                cat_coords_list = cat_depth_raw_mean_list = cls_ids_list = []
                contact_masks_debug_im = closest_mask_debug_im = None
                nearby_classes = {}
                segpred_display = depth_display = None

                seg_overlay = segmentation_overlay(rgb_frame, seg_result, 0.5)
                
                if detection_outputs:
                    contact_classes, depth_display, segpred_display, \
                        contact_masks_debug_im, closest_mask_debug_im, \
                        nearby_classes, \
                        cat_coords_list, cat_depth_raw_mean_list, cls_ids_list = self.localization.predict(detection_outputs, rgb_frame, depth_raw, depth_cm, reference_depth_raw, segpred_im=seg_result, seg_overlay=seg_overlay)

                self.publish_to_open3d_visualizer({
                    'rgb': rgb_frame,
                    'd': depth_raw,
                    'seg': None,
                    'cat_coords_list': cat_coords_list,
                    'depth_raw_mean_list': cat_depth_raw_mean_list,
                    'cls_ids_list': cls_ids_list
                })

                # debug images

                if self.args.debug_localization:
                    if contact_masks_debug_im is not None:
                        h, w = contact_masks_debug_im.shape
                        contact_masks_debug_im = np.tile(np.expand_dims(contact_masks_debug_im, axis=-1), (1, 1, 3))
                        qt_contact_masks_debug_im = QtGui.QImage(contact_masks_debug_im.data, 
                                                        w, h, 
                                                        contact_masks_debug_im.strides[0], 
                                                        QtGui.QImage.Format_RGB888)
                        self.debug_signal_1.emit(qt_contact_masks_debug_im)
                    if closest_mask_debug_im is not None:
                        h, w = closest_mask_debug_im.shape
                        closest_mask_debug_im = np.tile(np.expand_dims(closest_mask_debug_im, axis=-1), (1, 1, 3))
                        qt_closest_mask_debug_im = QtGui.QImage(closest_mask_debug_im.data, 
                                                        w, h, 
                                                        closest_mask_debug_im.strides[0], 
                                                        QtGui.QImage.Format_RGB888)
                        self.debug_signal_2.emit(qt_closest_mask_debug_im)
                else:
                    # for debug-1
                    if depth_display is None:
                        depth_display = depth_cm

                    # depth_display = cv2.resize(depth_display, dsize=(640, 480), interpolation=cv2.INTER_LINEAR)
                    height, width, _ = depth_display.shape
                    qt_depth_image = QtGui.QImage(depth_display.data,
                                            width,
                                            height,
                                            depth_display.strides[0],   
                                            QtGui.QImage.Format_RGB888)
                    self.debug_signal_1.emit(qt_depth_image)

                    # for debug-2
                    if segpred_display is None:
                        segpred_display = cv2.cvtColor(seg_overlay, cv2.COLOR_BGR2RGB)
                    else:
                        segpred_display = cv2.cvtColor(segpred_display, cv2.COLOR_BGR2RGB)

                    qt_seg_image = QtGui.QImage(segpred_display.data, 640, 480, segpred_display.strides[0], QtGui.QImage.Format_RGB888)
                    self.debug_signal_2.emit(qt_seg_image)
            
                self.widget.setLocalizationResultOnStatusLabel(nearby_classes)