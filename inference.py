import torch
import torch.nn as nn
from torch.utils.serialization import load_lua
from PIL import Image
import numpy as np
import cv2
import os
import unet as un
from utils import *
from convert_my_data import reshape_nyu_rgb, reshape_sun_depth

inference_path = "data2"
output_path = "result"

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


def inference_rgb(model, rgb_data):   
    scaled_rgb = reshape_nyu_rgb(rgb_data)
    scaled_rgb = np.expand_dims(scaled_rgb,0)
    torch_rgb = torch.tensor(scaled_rgb,dtype=torch.float32)
    
    if on_gpu:
        pred = model.forward(torch_rgb.cuda())
        pred_numpy = pred.cpu().detach().numpy()
    else:
        pred = model.forward(torch_rgb)
        pred_numpy = pred.detach().numpy()

    new_pred = np.argmax(pred_numpy[0],axis=0)

    return new_pred


def inference_batch(model_path, data_path, depth=False):
    print('Model folder:{}'.format(model_path))
    print('Data folder:{}'.format(data_path))

    unet = get_network(model_path, depth)
    unet.eval()
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    model_name = model_path.split('/')[1]
    
    img_ids = list()
    for i in os.listdir(data_path):
        if i.endswith('.npy'):
            img_ids.append(i.split('.')[0].split('_')[0])
    img_ids = list(set(img_ids))

    for img_id in img_ids:
        try:
            scaled_rgb = np.load(data_path + '/{}_RGB.npy'.format(img_id))
            scaled_depth = np.load(data_path + '/{}_DEPTH.npy'.format(img_id))
        except Exception as e:
            print(e)
            continue
        scaled_rgb = np.expand_dims(scaled_rgb,0)
        scaled_depth = np.expand_dims(scaled_depth,0)
        torch_rgb = torch.tensor(scaled_rgb,dtype=torch.float32)
        torch_depth = torch.tensor(scaled_depth,dtype=torch.float32)
        if on_gpu:
            if depth:
                pred = unet.forward((torch_rgb.cuda(),torch_depth.cuda()))
            else:
                pred = unet.forward(torch_rgb.cuda())
            pred_numpy = pred.cpu().detach().numpy()
        else:
            if depth:
                pred = unet.forward((torch_rgb,torch_depth))
            else:
                pred = unet.forward(torch_rgb)
            pred_numpy = pred.detach().numpy()

        new_pred = np.argmax(pred_numpy[0],axis=0)

        np.save(output_path + "/" + img_id + "_" + model_name, new_pred)


if __name__ == "__main__":
    os.makedirs(output_path, exist_ok=True)

    #inference_batch('models/nyu_rgb_no_pretrain', inference_path, depth=False)
    #inference_batch('models/nyu_rgb_imagenet_pretrain', inference_path,depth=False)
    inference_batch('models/nyu_rgb_scenenet_pretrain', inference_path, depth=False)
    #inference_batch('models/nyu_rgbd_no_pretrain', inference_path,depth=True)
    inference_batch('models/nyu_rgbd_scenenet_pretrain', inference_path,depth=True)

    #inference_batch('models/sun_rgb_no_pretrain',inference_path, depth=False)
    #inference_batch('models/sun_rgb_imagenet_pretrain', inference_path, depth=False)
    inference_batch('models/sun_rgb_scenenet_pretrain', inference_path, depth=False)
    #inference_batch('models/sun_rgbd_no_pretrain', inference_path, depth=True)
    inference_batch('models/sun_rgbd_scenenet_pretrain', inference_path, depth=True)
