import os
import cv2
import numpy as np

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

coco_class_names = {}
beammice_class_names = {}

with open('./tracking/detector/YOLOv3/data/beammice.names') as f:
    for i, line in enumerate(f.readlines()):
        class_name = line.strip()
        beammice_class_names[i] = class_name

with open('./tracking/detector/YOLOv3/data/coco.names') as f:
    for i, line in enumerate(f.readlines()):
        class_name = line.strip()
        coco_class_names[i] = class_name

def compute_color_for_labels(label):
    """
    Simple function that adds fixed color depending on the class
    """
    color = [int((p * (label ** 2 - label + 10)) % 255) for p in palette]
    return tuple(color)

def draw_boxes(img, bbox, identities=None, offset=(0,0), class_names=None, mode=None, nearby_classes=None):
    for i,box in enumerate(bbox):
        x1,y1,x2,y2 = [int(i) for i in box]
        x1 += offset[0]
        x2 += offset[0]
        y1 += offset[1]
        y2 += offset[1]
        # box text and bar
        id = int(identities[i]) if identities is not None else 0

        color_id = id
        if id == -1:
            color_id = 70
        elif id == 0:
            color_id = 1
        elif id == 1:
            color_id = 10
        elif id == 2:
            color_id = 20
        elif id == 3:
            color_id = 30

        color = compute_color_for_labels(color_id)

        if nearby_classes is not None:
            pass
        elif class_names is not None:
            if mode is None:
                label = '{}{:d}'.format("", id)
                if class_names == 'beammice':
                    class_id = int(label)
                    if class_id in beammice_class_names:
                        if mode is None:
                            label = beammice_class_names[class_id]
                elif class_names == 'coco':
                    class_id = int(label)
                    if class_id in coco_class_names:
                        if mode is None:
                            label = coco_class_names[class_id]
        
            elif mode == 'id':
                if id == -1:
                    label = '?'
                else:
                    label = 'pet-{:d}'.format(id)

        t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 2 , 2)[0]
        cv2.rectangle(img,(x1, y1),(x2,y2),color,3)
        cv2.rectangle(img,(x1-2, y1-t_size[1]-4),(x1+t_size[0],y1), color,-1)
        cv2.putText(img,label,(x1,y1-t_size[1]+16), cv2.FONT_HERSHEY_PLAIN, 2, [255,255,255], 2)

    return img

def draw_dot(img, pet_id, color, pet_pos):
    overlay = img.copy()
    cv2.circle(overlay, pet_pos, 8, color, -1)
    img = cv2.addWeighted(overlay, 0.3, img, 0.7, 0)
    #roi = img[pet_pos[1]:pet_pos[1]+10, pet_pos[0]: pet_pos[0]+10]
    #circle1 = cv2.circle(roi, (0, 0), 2, (255, 255, 255), thickness=-1)
    #circle2 = cv2.circle(roi, (0, 0), 2, color, thickness=-1)
    #blended = cv2.addWeighted(circle1, 0.5, circle2, 0.5)
    #img[pet_pos[1]:pet_pos[1]+10, pet_pos[0]: pet_pos[0]+10] = blended
    return img

def draw_trajectories(img, trajectories, dot=False):

    for pet_id, pos_list in trajectories.items():
        if pet_id == -1:
            color_id = 70
        elif pet_id == 0:
            color_id = 1
        elif pet_id == 1:
            color_id = 10
        elif pet_id == 2:
            color_id = 20
        elif pet_id == 3:
            color_id = 30
        else:
            color_id = pet_id
        color = compute_color_for_labels(color_id)

        if dot is False:
            if len(pos_list) == 1:
                break

            for i in range(len(pos_list)):
                if i == len(pos_list) - 1:
                    break
                img = cv2.line(img, pos_list[i], pos_list[i+1], color, thickness=2)
        else:
            for i in range(len(pos_list)):
                img = draw_dot(img, pet_id, color, pos_list[i])

    return img

if __name__ == '__main__':
    for i in range(82):
        print(compute_color_for_labels(i))
