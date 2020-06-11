from PIL import Image
import numpy as np
import cv2
import os
import matplotlib.image as mpimg
from utils import *
from convert_color import *


source_path = "/home/ubuntu/data2/"
output_path = "result/"


# rgb + depth
img_ids = list()
for filename in os.listdir(source_path):
    if filename.endswith('.jpg'):
        img_ids.append(filename.split('.')[0].split('_')[0])
img_ids = list(set(img_ids))

for filename in img_ids:
    img_rgb = cv2.imread(source_path + filename + "_RGB.jpg")
    img_depth = cv2.imread(source_path + filename + "_DEPTH.jpg")
    merge = cv2.add(img_rgb, img_depth)
    mpimg.imsave(source_path + filename + "_SUM.jpg", merge)


# segmentation class
alpha = 0.8
for filename in os.listdir(output_path):
    if filename.endswith('.npy'):
        n = np.load(output_path + filename)
        np_seg = class_from_instance(n)
        #np_seg = cv2.resize(np_seg, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)
        np_rgb = cv2.imread(source_path + filename.split('_')[0] + "_RGB.jpg")
        merge = cv2.addWeighted(np_rgb, alpha, np_seg, 1 - alpha, 0)
        mpimg.imsave(output_path + filename + ".jpg", merge)
