import numpy as np


# nyu class 13
color_code = np.array([[0, 0, 0], #UNKNOWN
                       [0, 0, 1], #BED
                       [0.9137,0.3490,0.1882], #BOOKS
                       [0, 0.8549, 0], #CEILING
                       [0.5843,0,0.9412], #CHAIR
                       [0.8706,0.9451,0.0941], #FLOOR
                       [1.0000,0.8078,0.8078], #FURNITURE
                       [0,0.8784,0.8980], #OBJECTS
                       [0.4157,0.5333,0.8000], #PAINTING
                       [0.4588,0.1137,0.1608], #SOFA
                       [0.9412,0.1373,0.9216], #TABLE
                       [0,0.6549,0.6118], #TV
                       [0.9765,0.5451,0], #WALL
                       [0.8824,0.8980,0.7608]]) #WINDOW


def class_from_instance(n):
    h, w = n.shape
    class_img_rgb = np.zeros((h,w,3),dtype=np.uint8)
    r = class_img_rgb[:,:,0]
    g = class_img_rgb[:,:,1]
    b = class_img_rgb[:,:,2]

    for instance_id in range(13):
        r[n==instance_id] = np.uint8(color_code[instance_id][0]*255)
        g[n==instance_id] = np.uint8(color_code[instance_id][1]*255)
        b[n==instance_id] = np.uint8(color_code[instance_id][2]*255)

    class_img_rgb[:,:,0] = r
    class_img_rgb[:,:,1] = g
    class_img_rgb[:,:,2] = b

    return class_img_rgb

