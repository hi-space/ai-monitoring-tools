#!/usr/bin/env python3

import cv2
import sys
import numpy as np
import argparse

import qtmodern.styles
import qtmodern.windows

from camera import RealSense, Camera, ToFrgb
from config import CameraConfig, RedisConfig
from utils import *

from pointcloud_service import PointCloudService
from segmentation_service import SegmentationService
from localization_service import LocalizationService
from detection_service import DetectionService
from video_service import VideoService

from ui.image_viewer import ImageViewer
from ui.rgbd_widget import RGBDWidget
from ui.segmentation_widget import SegmentationWidget
from ui.localization_widget import LocalizationWidget
from ui.pointcloud_widget import PointCloudWidget

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from debug.profiler import register_time_profiler_and_exec


def get_beammice_setup():

    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", action="store_true", default=False)
    parser.add_argument("--loc_seg_max_label", type=int, default=40)
    parser.add_argument("--loc_expand_lookup_region_as_ratio", type=float, default=0.0,
                        help="expand lookup region by ratio of (width, height) of image")
    parser.add_argument("--loc_contact_threshold", type=int,
                        default=800, help="300mm distance threshold")
    parser.add_argument("--enable_tof", action="store_true", default=False)
    parser.add_argument("--tof_device_no", type=int, default=3)
    parser.add_argument("--debug_localization",
                        action="store_true", default=False)

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = get_beammice_setup()

    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    main_window = QMainWindow()

    # Camera
    try:
        realsense_camera = RealSense()
        realsense_camera.start()

        if args.enable_tof:
            rgbtof_camera = ToFrgb(video_index=args.tof_device_no)
            rgbtof_camera.start()
    except Exception as e:
        print(e)
        sys.exit(app.exec_())

    # RealSense Video service & ui
    rs_video = VideoService(realsense_camera)
    rs_video.start()

    rs_rgbd_widget = RGBDWidget('Stereo')
    rs_rgb_siganl, rs_depth_signal = rs_rgbd_widget.getImageSignal()
    rs_rgbd_widget.setContentsMargins(QMargins(50, 20, 50, 20))

    rs_video.rgb_signal.connect(rs_rgb_siganl)
    rs_video.depth_signal.connect(rs_depth_signal)


    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, rs_rgbd_widget)

    # RGB TOF Video service & ui
    if args.enable_tof:
        rt_video = VideoService(rgbtof_camera)
        rt_video.start()

        rt_rgbd_widget = RGBDWidget('ToF')
        rt_rgb_siganl, rt_depth_signal = rt_rgbd_widget.getImageSignal()
        rt_rgbd_widget.setContentsMargins(QMargins(50, 20, 50, 20))

        rt_video.rgb_signal.connect(rt_rgb_siganl)
        rt_video.depth_signal.connect(rt_depth_signal)

        main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, rt_rgbd_widget)
        main_window.tabifyDockWidget(rs_rgbd_widget, rt_rgbd_widget)

    if CameraConfig.camera_mode == CameraConfig.CameraMode.REALSENSE:
        target_camera = realsense_camera

        # PointCloud service & ui
        pcd = PointCloudService(target_camera)
        pcd.start()

        pcd_widget = PointCloudWidget()
        pcd_widget.setButtonEvent(lambda: pcd.on(pcd_widget.isOn()))
        pcd_widget.setMouseEvent(pcd.camera.pcd.qt_mouse_event)
        pcd_widget.setContentsMargins(QMargins(50, 20, 50, 0))

        pcd.pcd_signal.connect(pcd_widget.getImageSignal())

        main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, pcd_widget)
    elif CameraConfig.camera_mode == CameraConfig.CameraMode.RGBTOF:
        target_camera = rgbtof_camera

    # Segmentation service & ui
    segmentation = SegmentationService(target_camera)
    segmentation.start()

    seg_widget = SegmentationWidget()
    seg_widget.setButtonEvent(lambda: segmentation.on(seg_widget.isOn()))
    seg_widget.setContentsMargins(QMargins(50, 20, 50, 20))

    seg_signal_1, seg_signal_2, seg_signal_3 = seg_widget.getImageSignal()
    segmentation.seg_signal_1.connect(seg_signal_1)
    segmentation.seg_signal_2.connect(seg_signal_2)
    segmentation.seg_signal_3.connect(seg_signal_3)

    main_window.setCentralWidget(seg_widget)

    # Detection service & ui
    detection = DetectionService(target_camera, segmentation)
    detection.start()

    localization_widget = LocalizationWidget()
    localization_widget.setButtonEvent(
        lambda: localization.on(localization_widget.isOn()))
    localization_widget.setContentsMargins(QMargins(50, 20, 50, 20))

    # Tracking service service & ui
    localization = LocalizationService(args, detection, segmentation,
                                       redis_conf=RedisConfig().conf,
                                       widget=localization_widget)
    localization.start()

    debug_signal_1, debug_signal_2 = localization_widget.getDebugSignal()

    detection.tracking_signal.connect(localization_widget.getImageSignal())

    localization.debug_signal_1.connect(debug_signal_1)
    localization.debug_signal_2.connect(debug_signal_2)

    main_window.addDockWidget(
        QtCore.Qt.RightDockWidgetArea, localization_widget)

    main_window.setContentsMargins(QMargins(50, 50, 50, 50))
    main_window.setWindowTitle("BeamMice")

    # main window theme
    main_window = qtmodern.windows.ModernWindow(main_window)
    main_window.show()

    if args.profile:
        register_time_profiler_and_exec(app)
    else:
        sys.exit(app.exec_())
