import cv2
import torch
import torch.nn as nn
from torch.utils.serialization import load_lua
import numpy as np
import os
import unet as un
from utils import *
from config import *
from convert_my_data import reshape_nyu_rgb, reshape_sun_depth
from color_mapping import *
from npy_to_image import segmentation_overlay
from camera import RealSense


def get_network(model_path):
    if model_path == (SUN_RGB_SCENENET_PRETRAIN or NYU_RGB_SCENENET_PRETRAIN):
        unet = un.UNet(14)

    if model_path == (SUN_RGBD_SCENENET_PRETRAIN or NYU_RGBD_SCENENET_PRETRAIN):
        unet = un.UNetRGBD(14)

    unet.load_state_dict(torch.load(model_path + '.pth'))

    if on_gpu:
        unet.cuda()

    return unet

def inference_rgb(mode, rgb_data):
    scaled_rgb = np.expand_dims(rgb_data,0)
    scaled_depth = np.expand_dims(depth_data,0)

    torch_rgb = torch.tensor(scaled_rgb,dtype=torch.float32)
    torch_depth = torch.tensor(scaled_depth,dtype=torch.float32)

    if on_gpu:
        pred = unet.forward(torch_rgb.cuda())
        pred_numpy = pred.cpu().detach().numpy()
    else:
        pred = unet.forward(torch_rgb)
        pred_numpy = pred.detach().numpy()

    new_pred = np.argmax(pred_numpy[0],axis=0)

    return new_pred

def inference_rgbd(model, rgb_data, depth_data):
    scaled_rgb = np.expand_dims(rgb_data,0)
    scaled_depth = np.expand_dims(depth_data,0)

    torch_rgb = torch.tensor(scaled_rgb,dtype=torch.float32)
    torch_depth = torch.tensor(scaled_depth,dtype=torch.float32)

    if on_gpu:
        pred = unet.forward((torch_rgb.cuda(),torch_depth.cuda()))
        pred_numpy = pred.cpu().detach().numpy()
    else:
        pred = unet.forward((torch_rgb,torch_depth))
        pred_numpy = pred.detach().numpy()

    new_pred = np.argmax(pred_numpy[0],axis=0)

    return new_pred


if __name__ == "__main__":
    camera = RealSense()
    camera.start()

    try:
        while True:
            rgb_frame, depth_frame = camera.get_frames()
            rgbd_frame = cv2.hconcat([rgb_frame, depth_frame])

            rgb_data = reshape_nyu_rgb(rgb_frame)
            depth_data = reshape_sun_depth(depth_frame[:,:,0])
            
            if unet.__class__ == un.UNet:
                np_seg = inference_rgb(unet, rgb_data)
            elif unet.__class__ == un.UNetRGBD:
                np_seg = inference_rgbd(unet, rgb_data, depth_data)
            
            seg_result = cv2.resize(class_from_instance(np_seg), dsize=(640, 480), interpolation=cv2.INTER_CUBIC)
            seg_overlay = segmentation_overlay(rgb_frame, np_seg, 0.5)
            seg = cv2.hconcat([seg_result, seg_overlay])

            rgbd_seg_result = cv2.vconcat([rgbd_frame, seg])

            cv2.namedWindow('rgbd_seg_result', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('rgbd_seg_result', rgbd_seg_result)

            cv2.waitKey(1)
    finally:
        camera.stop()


            
