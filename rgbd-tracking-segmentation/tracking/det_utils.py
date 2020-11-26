from debug.profiler import time_profiler

def get_custom_mask(cls_ids):
    
    # select person class
    # mask = cls_ids == 0

    # select cat class
    # 1) ./configs/yolov3.yaml
    # mask = cls_ids == 15
    # 2) ./configs/yolov3-beammice.yaml
    mask = (cls_ids >= 0) & (cls_ids <= 3)
    """
    bowl_mask = (cls_ids >= 4) & (cls_ids <= 8)
    pad_mask = (cls_ids == 9)
    """

    return mask

@time_profiler
def get_masked_det_outputs(detection_outputs, apply_custom_mask_function):

    if detection_outputs is None:
        raise ValueError("detection_outputs should not be None")

    bbox_xywh = detection_outputs.bbox_xywh
    cls_conf = detection_outputs.cls_conf
    cls_ids = detection_outputs.cls_ids

    mask = apply_custom_mask_function(cls_ids)

    bbox_xywh = bbox_xywh[mask]
    bbox_xywh[:,3:] *= 1.2 #  bbox dilation just in case bbox too small
    cls_conf = cls_conf[mask]
    cls_ids = cls_ids[mask]

    return bbox_xywh, cls_conf, cls_ids, True if any(mask) else False