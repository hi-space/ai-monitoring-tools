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


on_gpu = True


def get_network(model_path, depth=False):
    unet = un.UNetRGBD(14) if depth else un.UNet(14)
    unet.load_state_dict(torch.load(model_path + '.pth'))
    if on_gpu:
        unet.cuda()
    return unet


def inference_rgbd(model, rgb_data, depth_data):
    scaled_rgb = reshape_nyu_rgb(rgb_data)
    scaled_depth = reshape_sun_depth(depth_data)
    
    scaled_rgb = np.expand_dims(scaled_rgb,0)
    scaled_depth = np.expand_dims(scaled_depth,0)
    torch_rgb = torch.tensor(scaled_rgb,dtype=torch.float32)
    torch_depth = torch.tensor(scaled_depth,dtype=torch.float32)

    if on_gpu:
        pred = model.forward((torch_rgb.cuda(),torch_depth.cuda()))
        pred_numpy = pred.cpu().detach().numpy()
    else:
        pred = model.forward((torch_rgb,torch_depth))
        pred_numpy = pred.detach().numpy()

    new_pred = np.argmax(pred_numpy[0],axis=0)

    return new_pred


if __name__ == "__main__":
	unet = get_network(SUN_RGB_SCENENET_PRETRAIN, depth=False)
	
	camera = RealSense()
	
	while True:
		rgb_data, depth_data = camera.get_frames()
		
		# reshape

		np_seg = inference_rgbd(unet, rgb_data, depth_data)
		
