import numpy as np
import cv2
import os
from matplotlib.image as mpimg
from PIL import Image
from utils import *

source_path = ""
output_path = ""


def reshape_infer_rgb(n):
    img = Image.fromarray(n)
    img = img.resize(size=(320, 240))
    resized = np.array(img, dtype='float32')
    reshaped = np.transpose(resized, (2, 0, 1)) / 255.0
    return reshaped

def reshape_infer_depth(n):
    img = Image.fromarray(n)
    img = img.resize(size=(320, 240))
    resized = np.array(img, dtype='float32')
    reshaped = resized.reshape(1, 240, 320) / 10000.0
    return reshaped

for filename in os.listdir(PATH):
    if filename.endswith('RGB.npy'):
        # np
        img = reshape_infer_rgb(np.load(source_path + "/" + filename))
        n = np.array(img, dtype='float32')
        np.save(output_path + "/" + filename, n)

        # img
        np_img = reshape_img_rgb(n)
        save_np_to_image(output_path + "/" + filename + ".jpg", np_img)
    elif filename.endswith('DEPTH.npy'):
        # np
        img = reshape_infer_depth(np.load(source_path + "/" + filename))
        n = np.array(img, dtype='float32')
        np.save(output_path + "/" + filename, n)

        # img
        np_img = reshape_img_depth(n)
        save_np_to_image(output_path + "/" + filename + ".jpg", np_img)


