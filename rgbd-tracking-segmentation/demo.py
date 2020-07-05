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
    
    # Qt View
    rgb_viewer = ImageViewer()
    depth_viewer = ImageViewer()
    pcd_viewer = ImageViewer()
    seg_viewer = ImageViewer()
    tracking_viewer = ImageViewer()

    # Video thread
    video = VideoService(camera)
    video.rgb_signal.connect(rgb_viewer.setImage)
    video.depth_signal.connect(depth_viewer.setImage)

    video_thread = QtCore.QThread()
    video_thread.start()
    video.moveToThread(video_thread)

    # PCD Thread
    pcd = PointCloudService(camera)
    pcd.pcd_signal.connect(pcd_viewer.setImage)

    pcd_thread = QtCore.QThread()
    pcd_thread.start()
    pcd.moveToThread(pcd_thread)
    
    # Segmentation service thread
    segmentation = SegmentationService(camera)
    segmentation.seg_signal.connect(seg_viewer.setImage)

    segmentation_thread = QtCore.QThread()
    segmentation_thread.start()
    segmentation.moveToThread(segmentation_thread)

    # Tracking service thread
    tracking = TrackingService(camera)
    tracking.tracking_signal.connect(tracking_viewer.setImage)

    tracking_thread = QtCore.QThread()
    tracking_thread.start()
    tracking.moveToThread(tracking_thread)

    pcd_viewer.mouseMoveEvent = pcd.camera.pcd.qt_mouse_event

    # RGBD Dock Widget
    dw_rgbd_viewer = RGBDWidget(rgb_viewer, depth_viewer)
    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dw_rgbd_viewer)

    # Segmentation Dock Widget
    dw_seg_viewer = SegmentationWidget(seg_viewer)
    dw_seg_viewer.setButtonEvent(segmentation.start)
    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dw_seg_viewer)

    # Tracaking Dock Widget
    dw_tracking_viewer = LocalizationWidget(tracking_viewer)
    dw_tracking_viewer.setButtonEvent(tracking.start)
    main_window.setCentralWidget(dw_tracking_viewer)


    # PointCloud Dock Widget
    dw_pcd_viewer = PointCloudWidget(pcd_viewer)
    dw_pcd_viewer.setButtonEvent(pcd.start)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dw_pcd_viewer)
    
    # main_window.tabifyDockWidget(dw_rgb_viewer, dw_depth_viewer)
    
    # main window theme
    main_window = qtmodern.windows.ModernWindow(main_window)
    main_window.show()

    video.start()

    sys.exit(app.exec_())

