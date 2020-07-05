#!/usr/bin/env python3

import cv2
import sys
import numpy as np
import qtmodern.styles
import qtmodern.windows

from camera import RealSense
from config import CameraConfig
from pointcloud_service import PointCloudService
from segmentation_service import SegmentationService
from tracking_service import TrackingService
from ui.image_viewer import ImageViewer
from ui.rgbd_widget import RGBDWidget
from ui.segmentation_widget import SegmentationWidget
from ui.localization_widget import LocalizationWidget
from ui.pointcloud_widget import PointCloudWidget
from utils import *
from video_service import VideoService

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
    
    # Video thread & service & ui
    video_thread = QtCore.QThread()
    video_thread.start()

    video = VideoService(camera)

    rgbd_widget = RGBDWidget()
    rgb_siganl, depth_signal = rgbd_widget.getImageSignal()

    video.rgb_signal.connect(rgb_siganl)
    video.depth_signal.connect(depth_signal)

    video.moveToThread(video_thread)

    # PointCloud thread & service & ui
    pcd_thread = QtCore.QThread()
    pcd_thread.start()

    pcd = PointCloudService(camera)
    
    pcd_widget = PointCloudWidget()
    pcd_widget.setButtonEvent(pcd.start)
    pcd_widget.setMouseEvent(pcd.camera.pcd.qt_mouse_event)
    
    pcd.pcd_signal.connect(pcd_widget.getImageSignal())
    pcd.moveToThread(pcd_thread)

    # Segmentation thread & service & ui
    segmentation_thread = QtCore.QThread()
    segmentation_thread.start()

    segmentation = SegmentationService(camera)
    
    seg_widget = SegmentationWidget()
    seg_widget.setButtonEvent(segmentation.start)

    segmentation.seg_signal.connect(seg_widget.getImageSignal())
    segmentation.moveToThread(segmentation_thread)
    
    # Tracking service thread & service & ui
    tracking_thread = QtCore.QThread()
    tracking_thread.start()

    tracking = TrackingService(camera)
    
    tracking_widget = LocalizationWidget()
    tracking_widget.setButtonEvent(tracking.start)

    tracking.tracking_signal.connect(tracking_widget.getImageSignal())
    tracking.moveToThread(tracking_thread)

    # Dock Widgets
    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, rgbd_widget)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, pcd_widget)   
    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, seg_widget)
    main_window.setCentralWidget(tracking_widget)
    # main_window.tabifyDockWidget(dw_rgb_viewer, dw_depth_viewer)
    
    # main window theme
    main_window = qtmodern.windows.ModernWindow(main_window)
    main_window.show()

    video.start()

    sys.exit(app.exec_())

