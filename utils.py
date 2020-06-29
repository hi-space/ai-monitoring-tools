import numpy as np
import cv2
import matplotlib.image as mpimg
from PIL import Image

# nyu -> image
def reshape_img_rgb(n):
    cv2_rgb = np.uint8(np.transpose(n, (1, 2, 0)) * 255.0)
    cv2_bgr = cv2.cvtColor(cv2_rgb, cv2.COLOR_BGR2RGB)
    return cv2_bgr

def reshape_img_depth(n):
    np_depth = np.uint16(n[0] * 10000)
    return np_depth

def save_np_to_image(path, n):
    mpimg.imsave(path, n)

