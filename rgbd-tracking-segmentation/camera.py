import cv2
import matplotlib.pyplot as plt
import pyrealsense2 as rs
import numpy as np
from visualization.pointcloud import PointCloud

import sys
sys.path.append('./pmd_tof')

import argparse
import roypy
import time
import queue
from queue import Queue
from threading import Lock

from sample_camera_info import print_camera_info
from roypy_sample_utils import CameraOpener, add_camera_opener_options
from roypy_platform_utils import PlatformHelper
import matplotlib.pyplot as plt

from debug.tracer import pdb_pm

class ICamera():
    def __init__(self):
        pass
    
    def get_frames(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class Camera(ICamera):
    def __init__(self, stream_name=None, video_index=0):
        self.camera = None
        self.frame = None
        
        if stream_name is None:
            self.camera = cv2.VideoCapture(video_index)
        else:
            kvs = boto3.client("kinesisvideo")
            endpoint = kvs.get_data_endpoint(
                APIName="GET_HLS_STREAMING_SESSION_URL",
                StreamName=stream_name
            )['DataEndpoint']

            print(endpoint)

            kvam = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
            url = kvam.get_hls_streaming_session_url(
                StreamName=stream_name,
                PlaybackMode="LIVE"
            )['HLSStreamingSessionURL']

            self.camera = cv2.VideoCapture(url)
    
    def get_frames(self):
        try:
            ret, self.frame = self.camera.read()
        finally:
            return ret, self.frame, self.frame, None

class RealSense(ICamera):
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.align = rs.align(rs.stream.color)

        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30) # 640 480 

    def start(self):
        self.pipeline.start(self.config)
        self.profile = self.pipeline.get_active_profile()
        
        depth_sensor = self.profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()

        self.pcd = PointCloud(self.profile)

    def stop(self):
        self.pipeline.stop()

    def get_frames(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        self.depth_frame = aligned_frames.get_depth_frame()
        self.color_frame = aligned_frames.get_color_frame()

        self.depth_image = np.asanyarray(self.depth_frame.get_data())
        self.color_image = np.asanyarray(self.color_frame.get_data())
        self.depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(self.depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # self.color_image = cv2.cvtColor(self.color_image, cv2.COLOR_BGR2RGB)
        # self.color_image = self.color_image[0:480, 0:640]
        # self.depth_image = self.depth_image[0:480, 0:640] # cv2.resize(self.depth_image, (640, 480))
        # self.depth_colormap = self.depth_colormap[0:480, 0:640] # cv2.resize(self.depth_colormap, (640, 480))
        self.depth_image = cv2.resize(self.depth_image, (640, 480))
        self.color_image = cv2.resize(self.color_image, (640, 480))

        return True, self.color_image, self.depth_image, self.depth_colormap

    def get_pointcloud(self):
        out = self.pcd.update(self.color_frame, self.depth_frame, self.color_image, self.depth_colormap)
        return out

class MyListener(roypy.IDepthDataListener):
    def __init__(self, queue):
        super(MyListener, self).__init__()
        self.queue = queue

    def onNewData(self, data):
        zvalues = []
        for i in range(data.getNumPoints()):
            zvalues.append(data.getZ(i))
        zarray = np.asarray(zvalues)
        p = zarray.reshape (-1, data.width)
        self.queue.put(p)

class ToFrgb(ICamera):
    def __init__(self, video_index=0):
        super(ToFrgb, self).__init__()

        self.rgb_cam = cv2.VideoCapture(video_index)

        self.tof_queue = Queue(maxsize=1)
        self.l = MyListener(self.tof_queue)        

        import collections
        Options = collections.namedtuple("Options", "code rrf cal")
        options = Options(code="", rrf="", cal="")

        opener = CameraOpener(options)
        self.cam = opener.open_camera()
        #self.cam.setUseCase('MODE_5_45FPS_500')
        # self.cam.setUseCase('MODE_9_15FPS_700')
        print('Current PMD ToF use case: ', self.cam.getCurrentUseCase())
        print('Max frame rate: ', self.cam.getMaxFrameRate())
        print('Before: Current frame rate: ', self.cam.getFrameRate())
        # This does not work
        # self.cam.setFrameRate(45) 
        print('After: Current frame rate: ', self.cam.getFrameRate())
        self.cam.registerDataListener(self.l)

        self.pts1 = np.float32([[56,84],[109,85],[66,196],[120,193]])
        self.pts2 = np.float32([[247,248],[341,246],[256,461],[353,451]])
        self.M = cv2.getPerspectiveTransform(self.pts1, self.pts2)

        self.color_frame = None 

    def start(self):
        self.cam.startCapture()

    def stop(self):
        if hasattr(self, 'cam'):
           self.cam.stopCapture()

    def __del__(self):
       if hasattr(self, 'cam'):
           self.cam.stopCapture()

    def get_frames(self):

        try:
            self.depth_frame = self.tof_queue.get(True)
        except queue.Empty as e:
            return ret, self.color_frame, None, None

        ret, self.color_frame = self.rgb_cam.read()
        if ret == False:
            # print("Error: Camera is not detected properly.")
            return ret, None, None, None

        self.color_frame = self.color_frame[127:440, 106:496, :]
        self.color_frame = cv2.resize(self.color_frame, (640,480), cv2.INTER_LINEAR)

        if self.depth_frame is not None:
            self.depth_frame *= 1000
            self.depth_frame = self.depth_frame.astype('uint16')
            dst = cv2.warpPerspective(self.depth_frame, self.M, (640, 480))
            self.depth_frame = dst[94:397, 157:540] # [rows cols] ## Crop the perspective transformed depthmap for matching to the RGB image
            self.depth_frame = cv2.resize(self.depth_frame, (640,480), cv2.INTER_LINEAR)
            self.depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(self.depth_frame, alpha=0.04), cv2.COLORMAP_JET)
        else:
            self.depth_colormap = None

        self.color_frame = cv2.flip(self.color_frame, 0)
        self.color_frame = cv2.flip(self.color_frame, 1)

        self.depth_frame = cv2.flip(self.depth_frame, 0)
        self.depth_frame = cv2.flip(self.depth_frame, 1)

        self.depth_colormap = cv2.flip(self.depth_colormap, 0)
        self.depth_colormap = cv2.flip(self.depth_colormap, 1)

        return ret, self.color_frame, self.depth_frame, self.depth_colormap