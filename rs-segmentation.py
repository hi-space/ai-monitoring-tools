import cv2
import torch
import numpy as np

from camera import RealSense
from config import *
from convert_my_data import reshape_nyu_rgb, reshape_sun_depth
from color_mapping import *
from segmentation_model import SegmentationModel
from npy_to_image import segmentation_overlay


if __name__ == "__main__":
    camera = RealSense()
    camera.start()

    model = SegmentationModel(running_model, on_gpu, eval_mode)
    
    try:
        while True:
            try:
                rgb_frame, depth_frame, depth_colormap = camera.get_frames()
                
                rgbd_frame = cv2.hconcat([rgb_frame, depth_colormap])

                rgb_data = reshape_nyu_rgb(rgb_frame)
                depth_data = reshape_sun_depth(depth_frame)
                
                np_seg = model.inference(rgb_data, depth_data)
                
                seg_result = cv2.resize(class_from_instance(np_seg), dsize=(640, 480), interpolation=cv2.INTER_CUBIC)
                seg_overlay = segmentation_overlay(rgb_frame, np_seg, 0.5)
                seg = cv2.hconcat([seg_result, seg_overlay])

                rgbd_seg_result = cv2.vconcat([rgbd_frame, seg])

                cv2.namedWindow('rgbd_seg_result', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('rgbd_seg_result', rgbd_seg_result)

                cv2.waitKey(1)
            except Exception as e:
                print(e)
                pass

    finally:
        camera.stop()


            
