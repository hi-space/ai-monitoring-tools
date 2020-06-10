import numpy as np
import cv2
from PIL import Image

# nyu -> image
def reshape_npy_rgb(n):
    cv2_rgb = np.uint8(np.transpose(n, (1, 2, 0)) * 255.0)
    cv2_bgr = cv2.cvtColor(cv2_rgb, cv2.COLOR_BGR2RGB)
    return cv2_rgb

def reshape_npy_depth(n):
    np_depth = np.uint16(n[0] * 1000)
    return np_depth

# rs -> nyu
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
