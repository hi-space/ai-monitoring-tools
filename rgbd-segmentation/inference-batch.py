import cv2
import torch
import numpy as np
import os
from utils import *
from config import *
from convert_my_data import reshape_nyu_rgb, reshape_sun_depth
from segmentation_model import SegmentationModel


data_path = "data2"
output_path = "result"


def inference_batch(model, data_path=data_path, output_path=output_path):
    print('Model folder:{}'.format(model_path))
    print('Data Source folder:{}'.format(data_path))
    print('Inference Result folder:{}'.format(data_path))

    os.makedirs(output_path, exist_ok=True)
        
    img_ids = list()
    for i in os.listdir(data_path):
        if i.endswith('.npy'):
            img_ids.append(i.split('.')[0].split('_')[0])
    img_ids = list(set(img_ids))

    for img_id in img_ids:
        try:
            #rgb = cv2.imread(data_path + '/{}_RGB.jpg'.format(img_id))
            rgb = np.load(data_path + '/{}_RGB.npy'.format(img_id))
            depth = np.load(data_path + '/{}_DEPTH.npy'.format(img_id))
        except Exception as e:
            print(e)
            continue

        np_seg = model.inference(rgb, depth)

        np.save(output_path + "/" + img_id, np_seg)


if __name__ == "__main__":
    model = SegmentationModel(running_model, on_gpu, eval_mode)
    inference_batch(model, data_path, output_path)
