import copy

def xyxy_to_xywh(bbox_xywh, deepcopy=False):
    if deepcopy:
        det_bbox_xyxy = copy.deepcopy(bbox_xywh)
    else:
        det_bbox_xyxy = bbox_xywh 

    det_bbox_xyxy[:, 0] = bbox_xywh[:, 0] - bbox_xywh[:, 2] // 2
    det_bbox_xyxy[:, 1] = bbox_xywh[:, 1] - bbox_xywh[:, 3] // 2
    det_bbox_xyxy[:, 2] = bbox_xywh[:, 0] + bbox_xywh[:, 2] // 2
    det_bbox_xyxy[:, 3] = bbox_xywh[:, 1] + bbox_xywh[:, 3] // 2
    return det_bbox_xyxy

def get_valid_bboxes(bbox_XYXY, xmin_xmax_ymin_ymax):
    x1, y1, x2, y2 = bbox_XYXY
    xmin, xmax, ymin, ymax = xmin_xmax_ymin_ymax

    x1 = x1 if x1 >= xmin else xmin
    x2 = x2 if x2 <= xmax else xmax
    y1 = y1 if y1 >= ymin else ymin
    y2 = y2 if y2 <= ymax else ymax

    return x1, y1, x2, y2

def get_center_from_bbox(bbox_XYXY):
    (x1, y1, x2, y2) = bbox_XYXY
    return ((y1 + y2) // 2, (x1 + x2) // 2)