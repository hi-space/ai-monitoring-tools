import torch
import torch.nn as nn
from torch.utils.serialization import load_lua
from PIL import Image
import numpy as np
import cv2
import os
import unet as un

on_gpu = True

def inference(model_folder, inference_foler, depth=False):
    print('Model folder:{}'.format(model_folder))
    print('Inference folder:{}'.format(inference_foler))

    unet = un.UNetRGBD(14) if depth else un.UNet(14)
    unet.load_state_dict(torch.load(os.path.join(model_folder,'converted_clean_model.pth')))
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
        except:
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

inference_path = "my_data"
inference(model_folder='nyu_models/rgb_no_pretrain', inference_foler=inference_path, depth=False)
inference('nyu_models/rgb_imagenet_pretrain', inference_path,depth=False)
inference('nyu_models/rgb_scenenet_pretrain', inference_path, depth=False)
inference('nyu_models/rgbd_no_pretrain', inference_path,depth=True)
inference('nyu_models/rgbd_scenenet_pretrain', inference_path,depth=True)

inference('sun_models/rgb_no_pretrain',inference_path, depth=False)
inference('sun_models/rgb_imagenet_pretrain', inference_path, depth=False)
inference('sun_models/rgb_scenenet_pretrain', inference_path, depth=False)
inference('sun_models/rgbd_no_pretrain', inference_path, depth=True)
inference('sun_models/rgbd_scenenet_pretrain', inference_path, depth=True)
