#!/usr/bin/env python3

import argparse
import cv2
import sys
import numpy as np

from camera import ToFrgb
from utils import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--tof_device_no", type=int, default=4)
    args = parser.parse_args()

    try:
        rgbtof_camera = ToFrgb(video_index=args.tof_device_no)
        rgbtof_camera.start()
    except:
        print("Camera is not connected")
        sys.exit(1)

    try:
        while True:
            ret, color_image, _, depth_image = rgbtof_camera.get_frames()
            if ret == False:
                print('ret is false')
                continue
            
            rgbd_image = np.vstack([color_image, depth_image])
            cv2.namedWindow("BeamMice-ToF", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("BeamMice-ToF", rgbd_image)
            cv2.waitKey(1)

    finally:
        rgbtof_camera.stop()

