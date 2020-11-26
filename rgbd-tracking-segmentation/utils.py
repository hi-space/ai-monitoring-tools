import cv2
import time
import numpy as np

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from threading import Lock


def get_current_time():
    return time.strftime("%m-%d %H:%M:%S", time.gmtime())


def createImageWithOverlay(baseImage, overlayImage):
    imageWithOverlay = QtGui.QImage(baseImage.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
    painter = QtGui.QPainter(imageWithOverlay)

    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
    painter.fillRect(imageWithOverlay.rect(), QtCore.Qt.transparent)

    painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
    painter.drawImage(0, 0, baseImage)

    painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
    painter.drawImage(0, 0, overlayImage)

    painter.end()
    
    return imageWithOverlay


def rgba2rgb( rgba, background=(255,255,255) ):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros( (row, col, 3), dtype='float32' )
    r, g, b, a = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]

    a = np.asarray( a, dtype='float32' ) / 255.0

    R, G, B = background

    rgb[:,:,0] = r * a + (1.0 - a) * R
    rgb[:,:,1] = g * a + (1.0 - a) * G
    rgb[:,:,2] = b * a + (1.0 - a) * B

    return np.asarray( rgb, dtype='uint8' )


def update_overlay(baseImage):
    painter = QtGui.QPainter(baseImage)

    rec = QtGui.QPen(QtCore.Qt.red)
    painter.setPen(rec)

    painter.drawRect(10, 10, 20, 20)

    return qimage


def cv2qimage(image, w=640, h=480):    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, dsize=(w, h), interpolation=cv2.INTER_LINEAR)
    qt_image = QtGui.QImage(image.data,
                            w,
                            h,
                            image.strides[0],
                            QtGui.QImage.Format_RGB888)
        
    return qt_image

def title_text(text=""):
    label = QLabel(text)
    label.setStyleSheet("color: white;")
    label.setFixedHeight(70)
    label.setFont(QFont('Arial', 15, weight=QFont.Bold))
    label.setMargin(20)
    label.setAlignment(Qt.AlignCenter)
    return label

def description_text(text=""):
    label = QLabel(text)
    label.setStyleSheet("color: white;")
    label.setMargin(5)
    label.setAlignment(Qt.AlignCenter)
    return label
    
def xyxy_to_xywh(self, bbox_xywh, deepcopy=False):
    if deepcopy:
        det_bbox_xyxy = copy.deepcopy(bbox_xywh)
    else:
        det_bbox_xyxy = bbox_xywh 

    det_bbox_xyxy[:, 0] = bbox_xywh[:, 0] - bbox_xywh[:, 2] // 2
    det_bbox_xyxy[:, 1] = bbox_xywh[:, 1] - bbox_xywh[:, 3] // 2
    det_bbox_xyxy[:, 2] = bbox_xywh[:, 0] + bbox_xywh[:, 2] // 2
    det_bbox_xyxy[:, 3] = bbox_xywh[:, 1] + bbox_xywh[:, 3] // 2
    return det_bbox_xyxy

def get_valid_bbox_indices(self, bbox_XYXY, xmin_xmax_ymin_ymax):
    x1, y1, x2, y2 = bbox_XYXY
    xmin, xmax, ymin, ymax = xmin_xmax_ymin_ymax

    x1 = x1 if x1 >= xmin else xmin
    x2 = x2 if x2 <= xmax else xmax
    y1 = y1 if y1 >= ymin else ymin
    y2 = y2 if y2 <= ymax else ymax

    return x1, y1, x2, y2

def get_center_from_bbox(self, bbox_XYXY):
    (x1, y1, x2, y2) = bbox_XYXY
    return ((y1 + y2) // 2, (x1 + x2) // 2)
