from PIL import Image
import numpy as np
import cv2
import os
import matplotlib.image as mpimg
from utils import *


source_path = "/home/ubuntu/data2"
output_path = "/home/ubuntu/result"

img_ids = list()
for filename in os.listdir(source_path):
    if filename.endswith('.jpg')
        img_ids.append(filename.split('.')[0].split('_')[0])
img_ids = list(set(img_ids))

for filename in img_ids:
    img_rgb = cv2.imread(source_path + filename + "_RGB.jpg")
    img_depth = cv2.imread(source_path + filename + "_DEPTH.jpg")
    img_rgb = cv2.resize(img_rgb, dsize=(320, 240))
    img_depth = cv2.resize(img_depth, dsize=(320, 240))
    merge = cv2.add(img_rgb, img_depth)
    mpimg.imsave(source_path + filename + "_SUM.jpg", merge)

    model_name = ""
    output_file = output_path + filename + "_" + model_name

    # np to img
    n = np.load(output_file + ".npy")
    save_np_to_image(output_file + ".jpg", n)

    # img merge
    result = cv2.add(img_rgb, cv2.imread(output_file + ".jpg"))
    mpimg.imsave(output_file + "_RESULT.jpg")

