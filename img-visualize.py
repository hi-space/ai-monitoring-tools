from PIL import Image
import numpy as np
import cv2
import os
import matplotlib.image as mpimg
from utils import *
from convert_color import *


source_path = "data/"
output_path = "result/"


# ids
img_ids = list()
for filename in os.listdir(source_path):
    if filename.endswith('.npy'):
        img_ids.append(filename.split('.')[0].split('_')[0])
img_ids = list(set(img_ids))


def rgbd_npy_to_image(alpha=0.7):
    for filename in img_ids:
       np_rgb = np.load(source_path + filename + "_RGB.npy")
       img_rgb = Image.fromarray(np_rgb)
       mpimg.imsave(source_path + filename + "_RGB.jpg", np_rgb)

       # depth
       np_depth = np.load(source_path + filename + "_DEPTH.npy")
       norm_depth = cv2.normalize(np_depth, None, 0, 255, cv2.NORM_MINMAX)
       cvt_depth = cv2.cvtColor(norm_depth, cv2.COLOR_GRAY2BGR)
       np_depth = cvt_depth.astype(np.uint8)
       mpimg.imsave(source_path + filename + "_DEPTH.jpg", np_depth)

       # rgb + depth
       alpha = 0.7
       merge = cv2.addWeighted(np_rgb, alpha, np_depth, 1 - alpha, 0)
       mpimg.imsave(source_path + filename + "_SUM.jpg", merge)


# segmentation class
def infer_npy_to_image(alpha=0.8):
    alpha = 0.8
    for filename in os.listdir(output_path):
        if filename.endswith('.npy'):
            n = np.load(output_path + filename)
            np_seg = class_from_instance(n)
            np_seg = cv2.resize(np_seg, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)
            np_rgb = cv2.imread(source_path + filename.split('_')[0] + "_RGB.jpg")
            merge = cv2.addWeighted(np_rgb, alpha, np_seg, 1 - alpha, 0)
            mpimg.imsave(output_path + filename + ".jpg", merge)



if __name__ == "__main__":
    #infer_npy_to_image(0.5)
    rgbd_npy_to_image(0.5)
