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

    # Qt View
    rgb_viewer = ImageViewer()
    depth_viewer = ImageViewer()
    pcd_viewer = ImageViewer()
    seg_viewer = ImageViewer()
    tracking_viewer = ImageViewer()

    seg_button = QPushButton('Segmentation')
    tracking_button = QPushButton('Tracking')
    pcd_button = QPushButton('PointCloud')

    pcd_viewer.mouseMoveEvent = pcd.camera.pcd.qt_mouse_event

    # RGBD Dock Widget
    rgbd_layout = QHBoxLayout()
    rgbd_layout.addWidget(rgb_viewer)
    rgbd_layout.addWidget(depth_viewer)

    rgbd_widget = QWidget()
    rgbd_widget.setLayout(rgbd_layout)

    dw_rgbd_viewer = QDockWidget()
    dw_rgbd_viewer.setWindowTitle('RGBD')
    dw_rgbd_viewer.setWidget(rgbd_widget)

    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dw_rgbd_viewer)


    # Segmentation Dock Widget
    seg_layout = QVBoxLayout()
    seg_layout.addWidget(seg_viewer)
    seg_layout.addWidget(seg_button)
    
    seg_widget = QWidget()
    seg_widget.setLayout(seg_layout)

    dw_seg_viewer = QDockWidget()
    dw_seg_viewer.setWindowTitle('Segmentation')
    dw_seg_viewer.setWidget(seg_widget)
    
    main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dw_seg_viewer)


    # Tracking Dock Widget
    status_bar = QStatusBar()
    
    status_label = QLabel("cat is on the table")
    status_label.setFixedSize(640, 100)
    status_label.setStyleSheet("color: white;")
    status_label.setFont(QtGui.QFont('Arial', 15))
    status_label.setAlignment(Qt.AlignCenter)

    status_bar.addWidget(status_label)
    
    tracking_layout = QVBoxLayout()
    tracking_layout.addWidget(tracking_viewer)
    tracking_layout.addWidget(status_bar)
    tracking_layout.addWidget(tracking_button)
    

    tracking_widget = QWidget()
    tracking_widget.setLayout(tracking_layout)

    dw_tracking_viewer = QDockWidget()
    dw_tracking_viewer.setWindowTitle('Tracking')
    dw_tracking_viewer.setWidget(tracking_widget)
    
    main_window.setCentralWidget(dw_tracking_viewer)


    # PointCloud Dock Widget
    pcd_layout = QVBoxLayout()
    pcd_layout.addWidget(pcd_viewer)
    pcd_layout.addWidget(pcd_button)

    pcd_widget = QWidget()
    pcd_widget.setLayout(pcd_layout)

    dw_pcd_viewer = QDockWidget()
    dw_pcd_viewer.setWindowTitle('PointCloud')
    dw_pcd_viewer.setWidget(pcd_widget)

    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dw_pcd_viewer)
    
    # main_window.tabifyDockWidget(dw_rgb_viewer, dw_depth_viewer)


    # Button Event
    pcd_button.clicked.connect(pcd.start)
    seg_button.clicked.connect(segmentation.start)
    tracking_button.clicked.connect(tracking.start)

    
    # main window theme
    main_window = qtmodern.windows.ModernWindow(main_window)
    main_window.show()

    video.start()
    # pcd.start()
    # segmentation.start()
    # tracking.start()

    sys.exit(app.exec_())
