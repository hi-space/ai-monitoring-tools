import torch
import torch.nn as nn
from torch.utils.serialization import load_lua
from PIL import Image
import numpy as np
import cv2
import os
import unet as un
from utils import *


inference_path="/home/ubuntu/data"

on_gpu = True

def inference(model_folder, inference_foler, depth=False):
    print('Model folder:{}'.format(model_folder))
    print('Inference folder:{}'.format(inference_foler))

    unet = un.UNetRGBD(14) if depth else un.UNet(14)
    unet.load_state_dict(torch.load(model_folder + '.pth'))
    if on_gpu:
        unet.cuda()
    unet.eval()
    
    output_folder = inference_foler + "/" + model_folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    img_ids = list()
    for i in os.listdir(inference_foler):
        if i.endswith('.npy'):
            img_ids.append(i.split('.')[0].split('_')[0])
    img_ids = list(set(img_ids))

    for img_id in img_ids:
        try:
            scaled_rgb = np.load(inference_foler + '/{}_RGB.npy'.format(img_id))
            scaled_depth = np.load(inference_foler + '/{}_DEPTH.npy'.format(img_id))
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
    
        np.save(output_folder + '/' + img_id, new_pred)

inference('models/nyu_rgb_no_pretrain', inference_path, depth=False)
inference('models/nyu_rgb_imagenet_pretrain', inference_path,depth=False)
inference('models/nyu_rgb_scenenet_pretrain', inference_path, depth=False)
inference('models/nyu_rgbd_no_pretrain', inference_path,depth=True)
inference('models/nyu_rgbd_scenenet_pretrain', inference_path,depth=True)

inference('models/sun_rgb_no_pretrain',inference_path, depth=False)
inference('models/sun_rgb_imagenet_pretrain', inference_path, depth=False)
inference('models/sun_rgb_scenenet_pretrain', inference_path, depth=False)
inference('models/sun_rgbd_no_pretrain', inference_path, depth=True)
inference('models/sun_rgbd_scenenet_pretrain', inference_path, depth=True)
