#!/usr/bin/env python3

import cv2
import sys
import numpy as np
import qtmodern.styles
import qtmodern.windows

from camera import RealSense
from config import CameraConfig
from utils import *

from pointcloud_service import PointCloudService
from segmentation_service import SegmentationService
from localization_service import LocalizationService
from video_service import VideoService

from ui.image_viewer import ImageViewer
from ui.rgbd_widget import RGBDWidget
from ui.segmentation_widget import SegmentationWidget
from ui.localization_widget import LocalizationWidget
from ui.pointcloud_widget import PointCloudWidget

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    main_window = QMainWindow()
    
    # Camera
    try:
        if CameraConfig.camera_mode == CameraConfig.CameraMode.REALSENSE:
            camera = RealSense()
            camera.start()
        elif CameraConfig.camera_mode == CameraConfig.CameraMode.RGBTOF:
            pass
    except Exception as e:
        print(e)
        sys.exit(app.exec_())
    
    # Video service & ui
    video = VideoService(camera)
    video.start()

    rgbd_widget = RGBDWidget()
    rgb_siganl, depth_signal = rgbd_widget.getImageSignal()

    video.rgb_signal.connect(rgb_siganl)
    video.depth_signal.connect(depth_signal)

    # PointCloud service & ui
    pcd = PointCloudService(camera)
    pcd.start()
    
    pcd_widget = PointCloudWidget()
    pcd_widget.setButtonEvent(lambda: pcd.on(pcd_widget.isOn()))
    pcd_widget.setMouseEvent(pcd.camera.pcd.qt_mouse_event)
    
    pcd.pcd_signal.connect(pcd_widget.getImageSignal())

    # Segmentation service & ui
    segmentation = SegmentationService(camera)
    segmentation.start()
    
    seg_widget = SegmentationWidget()
    # seg_widget.setButtonEvent(lambda: segmentation.on(seg_widget.isOn()))
    seg_widget.setButtonEvent(lambda: segmentation.run())

    seg_signal_1, seg_signal_2, seg_signal_3, seg_signal_4 = seg_widget.getImageSignal()
    segmentation.seg_signal_1.connect(seg_signal_1)
    segmentation.seg_signal_2.connect(seg_signal_2)
    segmentation.seg_signal_3.connect(seg_signal_3)
    segmentation.seg_signal_4.connect(seg_signal_4)
    
    # Tracking service service & ui
    localization = LocalizationService(camera, segmentation)
    localization.start()
    
    localization_widget = LocalizationWidget()
    localization_widget.setButtonEvent(lambda: localization.on(localization_widget.isOn()))

    debug_signal_1, debug_signal_2 = localization_widget.getDebugSignal()

    localization.tracking_signal.connect(localization_widget.getImageSignal())
    localization.debug_signal_1.connect(debug_signal_1)
    localization.debug_signal_2.connect(debug_signal_2)

    # Dock Widgets
    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, rgbd_widget)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, pcd_widget)   
    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, seg_widget)
    main_window.setCentralWidget(localization_widget)
    # main_window.tabifyDockWidget(dw_rgb_viewer, dw_depth_viewer)
    
    # main window theme
    main_window = qtmodern.windows.ModernWindow(main_window)
    main_window.show()
    
    sys.exit(app.exec_())

