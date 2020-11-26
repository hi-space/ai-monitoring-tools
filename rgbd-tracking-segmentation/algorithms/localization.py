import os
import queue 
import copy
import random

import cv2
import numpy as np

from publisher import RedisPublisher
from tracking import bbox_utils, det_utils
from tracking.utils.draw import draw_boxes

from debug.profiler import time_profiler
from debug.tracer import pdb_trace, pdb_pm

class Localization(object):

    DOWNSCALE_RATIO = 4

    def __init__(self, args):
        self.args = args
        self.nearby_classes = None

    @time_profiler
    def get_cropped_depth_from_cats_bbox(self, depth_im, bbox_XYXY):
        (x1, y1, x2, y2) = bbox_XYXY
        return copy.deepcopy(depth_im[y1:y2+1, x1:x2+1])

    @time_profiler
    def get_depth_sampling_indices_close_to_cats_center(self, bbox_XYXY, centerYX, SAMPLE_NR_RATIO=0.85, SAMPLE_REGION_WIDTH_RATIO=0.2):
        
        (x1, y1, x2, y2) = bbox_XYXY
        SAMPLE_REGION_WH_RATIO = (y2 - y1) / (x2 - x1)
        # SAMPLE_REGION_WH_RATIO = 1.0
        sample_region_width = int((x2 - x1) * SAMPLE_REGION_WIDTH_RATIO)
        sample_region_height = int(SAMPLE_REGION_WH_RATIO * sample_region_width)
        SAMPLE_NR  = int(SAMPLE_NR_RATIO * sample_region_width * sample_region_height)
        
        sample_ymin_range, sample_ymax_range = (-sample_region_height, sample_region_height)
        sample_xmin_range, sample_xmax_range = (-sample_region_width, sample_region_width)

        indices = [(i, j) for i in range(sample_ymin_range, sample_ymax_range+1) for j in range(sample_xmin_range, sample_xmax_range+1)]
        # indices = random.sample(indices, SAMPLE_NR) # the number of samples = i

        sampled_indices = []
        for (y, x) in indices:
            sampled_indices.append((centerYX[0] + y, centerYX[1] + x)) # store sampled indices

        return sampled_indices

    @time_profiler
    def get_valid_bboxes_and_depth_samples(self, det_bbox_xyxy, rgb_im, depth_im):
        valid_bboxes_coord = []
        cat_info = []
        
        for bbox in det_bbox_xyxy.tolist():
            x1, y1, x2, y2 = (int(coord) for coord in bbox)
            x1, y1, x2, y2 = (x1//self.DOWNSCALE_RATIO, y1//self.DOWNSCALE_RATIO, x2//self.DOWNSCALE_RATIO, y2//self.DOWNSCALE_RATIO)
            x1, y1, x2, y2 = bbox_utils.get_valid_bboxes(bbox_XYXY=(x1, y1, x2, y2), xmin_xmax_ymin_ymax=(0, rgb_im.shape[1]//self.DOWNSCALE_RATIO-1, 0, rgb_im.shape[0]//self.DOWNSCALE_RATIO-1))

            if x1 == x2 or y1 == y2:
                continue

            # get center coordinate from detected bbox
            (cy, cx) = bbox_utils.get_center_from_bbox(bbox_XYXY=(x1, y1, x2, y2))

            # get crop depth image within the bbox 
            cat_cropped_depth = self.get_cropped_depth_from_cats_bbox(depth_im, bbox_XYXY=(x1, y1, x2, y2))

            # get samples for calculating cat's depth
            sampled_indices = self.get_depth_sampling_indices_close_to_cats_center(bbox_XYXY=(x1, y1, x2, y2), centerYX=(cy, cx))

            cat_info.append((cat_cropped_depth, sampled_indices))
            valid_bboxes_coord.append((x1, y1, x2, y2))

        return cat_info, valid_bboxes_coord

    @time_profiler
    def rule_out_samples_in_seg_area_within_bbox(self, sampled_indices, segpred_im, seglabels_list, bboxXYXY):
        
        # initial samples
        sampled_indices_set = {}
        for sampled_index in sampled_indices:
            sampled_indices_set[sampled_index] = True

        (x1, y1, x2, y2) = bboxXYXY

        # rule out all samples that are included in seglabels
        for seglabel in seglabels_list:
            x = np.where(segpred_im == seglabel)
            y_real_idx = []
            x_real_idx = []
            for y, x in zip(x[0].tolist(), x[1].tolist()):
                if (x1 <= x <= x2) and (y1 <= y <= y2):
                    y_real_idx.append(y)
                    x_real_idx.append(x)

            segarea_idx_set = zip(y_real_idx, x_real_idx)
            # sampled_indices_set = sampled_indices_set - segarea_idx_set

            for idx in segarea_idx_set:
                if idx in sampled_indices_set:
                    del sampled_indices_set[idx]

            del segarea_idx_set

        return sampled_indices_set.keys()

    @time_profiler
    def get_one_segment(self, init_pos, remain_set):
        dx, dy = [1, 0, -1, 0], [0, 1, 0, -1]
        visited = {}

        q = queue.Queue()

        q.put(init_pos)

        while not q.empty():
            pos = q.get()
            
            if pos in visited:
                continue

            visited[pos] = True

            (y, x) = pos

            for (deltay, deltax) in zip(dy, dx):
                next_pos = (y+deltay, x+deltax)
                if next_pos in remain_set.keys():
                    q.put(next_pos)

        return visited

    @time_profiler
    def find_disjoint_areas_and_calc_depths(self, remain_set, reference_depth_raw, seg_area_allow_min_pixels=10):

        # remain_set = copy.deepcopy(whole_set)
        segmented_mean_depth_vals = []
        segmented_areas = []
        while len(remain_set) > 0:
            init_pos = list(remain_set.keys())[0]
            segment_set = self.get_one_segment(init_pos, remain_set)
            segmented_areas.append(segment_set)
            depth_vals = []
            for (y, x) in segment_set:
                if reference_depth_raw[y, x] > 0:#  and reference_depth_raw[y, x] < 24000:
                    depth_vals.append(reference_depth_raw[y, x])

            # THe number of samples obtained from segmented region should be above the threshold
            if len(depth_vals) > seg_area_allow_min_pixels:
                depth_vals = np.asarray(depth_vals)
                mean_depth_vals = np.mean(depth_vals)
                segmented_mean_depth_vals.append(mean_depth_vals)

                import math
                if math.isnan(mean_depth_vals):
                    import pdb; pdb.set_trace()
                
                del depth_vals

            for pos in segment_set:
                if pos in remain_set:
                    del remain_set[pos]
            # remain_set -= segment_set
        
            del segment_set

        return segmented_mean_depth_vals, segmented_areas

    @time_profiler
    def draw_white_rect_on_img(self, display_in_bbox_XYXY, img):
        x1, y1, x2, y2 = display_in_bbox_XYXY
        sub_img = img[y1:y2+1, x1:x2+1]
        white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 255
        res = cv2.addWeighted(sub_img, 0.5, white_rect, 0.5, gamma=0)
        img[y1:y2+1, x1:x2+1] = res

    def id2name(self, cls_id):
        if cls_id == 5:
            return "floor"
        elif cls_id == 20:
            return "wall"
        else:
            return "objects"
            
    @time_profiler
    def predict(self, detection_outputs, rgb_im, depth_raw, depth_im_cmapped, reference_depth_raw, segpred_im=None, seg_overlay=None):

        # depth_im: depth for display only (needs conversion to uint8)
        depth_im = copy.deepcopy(depth_raw >> 5)
        depth_im = depth_im.astype('uint8')

        reference_depth_im = copy.deepcopy(reference_depth_raw >> 5)
        reference_depth_im = reference_depth_im.astype('uint8')

        depth_raw = cv2.resize(depth_raw, (640 // self.DOWNSCALE_RATIO, 480 // self.DOWNSCALE_RATIO))
        reference_depth_raw = cv2.resize(reference_depth_raw, (640 // self.DOWNSCALE_RATIO, 480 // self.DOWNSCALE_RATIO))

        # for display
        rgb_frame = cv2.cvtColor(rgb_im, cv2.COLOR_BGR2RGB)

        depth_display = copy.deepcopy(depth_im_cmapped)

        self.reference_depth_raw = copy.deepcopy(reference_depth_raw)
        self.reference_depth_im = copy.deepcopy(reference_depth_im)

        bbox_xywh, cls_conf, cls_ids, cat_detected = det_utils.get_masked_det_outputs(detection_outputs, det_utils.get_custom_mask)
        det_bbox_xyxy = bbox_utils.xyxy_to_xywh(bbox_xywh, deepcopy=True)
    
        cat_info, bboxes_coord = self.get_valid_bboxes_and_depth_samples(det_bbox_xyxy, rgb_frame, depth_im)

        if segpred_im is not None and segpred_im.shape == (240, 320) and seg_overlay is not None:
            segpred_im = segpred_im.astype('uint8')
            segpred_display = cv2.resize(seg_overlay, (640, 480))
            if (640 // self.DOWNSCALE_RATIO, 480 // self.DOWNSCALE_RATIO) != (320, 240):
                segpred_im = cv2.resize(segpred_im, (640 // self.DOWNSCALE_RATIO, 480 // self.DOWNSCALE_RATIO))
        else:
            segpred_display = None

        # return variables
        cat_coords_list = []
        cat_depth_raw_mean_list = []
        cls_ids_list = []
        pets_contact_classes = []

        show_only_first_valid_localization_result = True 
        for_display_v = []
        for_display_contacts = []
        first_valid_closest_mask = -1

        nearby_classes = {}

        for bbox_idx, item in enumerate(zip(cat_info, bboxes_coord, cls_ids.tolist())):

            if bbox_idx == 1:
                show_only_first_valid_localization_result = False

            (cat_info, (x1, y1, x2, y2), cls_id) = item
            in_bbox_indices = [(y, x) for y in range(y1, y2+1) for x in range(x1, x2+1)]
            display_in_bbox_XYXY = (x1 * self.DOWNSCALE_RATIO, y1 * self.DOWNSCALE_RATIO, x2 * self.DOWNSCALE_RATIO, y2 * self.DOWNSCALE_RATIO)

            if segpred_im is not None:
                (cat_cropped_depth, sampled_indices) = cat_info
                cat_coord = ((x1+x2)//2, (y1+y2)//2)
                cat_coords_list.append((cat_coord[0] * self.DOWNSCALE_RATIO, cat_coord[1] * self.DOWNSCALE_RATIO))
                # cat_coords_list.append(cat_coord)
                cls_ids_list.append(cls_id)

                segmented_area_with_depth = copy.deepcopy(segpred_im)

                closest_mask_idx = 0
                contact_classes = []
                closest_segmask = -1
                closest_depth_raw_mean_distance = 1e7
                closest_mask_candidates_idx = 0

                # using segmentation information, rule out the samples for cat's depth calculation that are included in the object area
                # NOTE
                cat_depth_sample_indices = self.rule_out_samples_in_seg_area_within_bbox(sampled_indices, segpred_im, seglabels_list=[40], bboxXYXY=(x1, y1, x2, y2))
                if len(cat_depth_sample_indices) == 0:
                    # The condition here means that the cat has been detected, but all samples are wiped out by the segmented areas
                    # which means that we can use all samples
                    cat_depth_sample_indices = sampled_indices

                depth_samples = []
                cat_samples_y_ind = []
                cat_samples_x_ind = []

                for y, x in cat_depth_sample_indices:
                    # NOTE: Avoid truncated zero depth values
                    if depth_raw[y, x] > 0:
                        depth_samples.append(depth_raw[y, x])
                        cat_cropped_depth[y-y1, x-x1] = 255 * 0.5

                        cat_samples_y_ind.append(y)
                        cat_samples_x_ind.append(x)

                if len(depth_samples) == 0:
                    continue

                cat_depth_raw_mean = np.mean(depth_samples)
                cat_depth_raw_mean_list.append(cat_depth_raw_mean)
            
                for j in range(1, self.args.loc_seg_max_label + 1):
                    h, w = segpred_im.shape
                    x = np.where(segpred_im == j)
                    y_real_idx = []
                    x_real_idx = []

                    expand_ratio = self.args.loc_expand_lookup_region_as_ratio

                    lookup_region = (x1 - int(expand_ratio * (x2 - x1)), y1 - int(expand_ratio * (y2 - y1)), \
                        x2 + int(expand_ratio * (x2 - x1)), y2 + int(expand_ratio * (y2 - y1)))
                    lookup_region = bbox_utils.get_valid_bboxes(bbox_XYXY=lookup_region, xmin_xmax_ymin_ymax=(0, w-1, 0, h-1))
            
                    for y, x in zip(x[0].tolist(), x[1].tolist()):
                        if (lookup_region[0] <= x <= lookup_region[2]) \
                            and (lookup_region[1] <= y <= lookup_region[3]):
                            y_real_idx.append(y)
                            x_real_idx.append(x)

                    p_idx_j = set(zip(y_real_idx, x_real_idx))
                    bbox_idx_set = set(in_bbox_indices)
                    hashed_inter = {}
                    inter = list(set.intersection(p_idx_j, bbox_idx_set))
                    for pos in inter:
                        hashed_inter[pos] = True

                    del bbox_idx_set

                    if len(inter) > 0:
                        segmask_raw_depth_vals = []

                        segmented_mean_depth_vals, segmented_areas = self.find_disjoint_areas_and_calc_depths(hashed_inter, self.reference_depth_raw)
                        del hashed_inter
                        if len(segmented_mean_depth_vals) == 0:
                            continue    

                        closest_mask_candidates_idx += 1 
                    
                        closest_depth_mean_distance_to_segment_regions = 1e7
                        closest_segmented_mean_depth = None

                        if self.args.debug_localization:
                            print('segmented mean depth values: ', segmented_mean_depth_vals)

                        closest_segmented_mean_depth_idx = -1
                        for i, segmented_mean_depth_val in enumerate(segmented_mean_depth_vals):
                            dist = abs(segmented_mean_depth_val - cat_depth_raw_mean)

                            if dist < closest_depth_mean_distance_to_segment_regions:
                                closest_depth_mean_distance_to_segment_regions = dist
                                closest_segmented_mean_depth = segmented_mean_depth_val
                                closest_segmented_mean_depth_idx = i

                        del segmented_mean_depth_vals

                        if closest_depth_mean_distance_to_segment_regions < closest_depth_raw_mean_distance:
                            closest_depth_raw_mean_distance = closest_depth_mean_distance_to_segment_regions
                            closest_mask_idx = closest_mask_candidates_idx - 1
                            closest_segmask = j

                        if self.args.debug_localization:
                            print('class [%s] - %d (depth proximity: %s)' % ("floor" if j == 5 else "object", len(p_idx_j), "True" if closest_depth_mean_distance_to_segment_regions <= self.args.loc_contact_threshold else "False"))
                            print('\__ cat\'s depth mean: %d' % (cat_depth_raw_mean))
                            print('\__ closest depth mean to other objects: %d' % (closest_segmented_mean_depth))
                            print('\__ mean abs dist: %d (threshold: %d)' % (closest_depth_mean_distance_to_segment_regions, self.args.loc_contact_threshold))

                        whether_cat_contacts = False
                        # for all adjacent segments, if the mean depth distance is below a certain threshold, we treat those classes as "contact classes"
                        if closest_depth_mean_distance_to_segment_regions <= self.args.loc_contact_threshold:
                            contact_classes.append(j)
                            whether_cat_contacts = True

                        if closest_segmented_mean_depth_idx != -1 and self.args.debug_localization:

                            inter_segpred_im = copy.deepcopy(segpred_im)
                            for (y, x) in p_idx_j: #inter: # segmented_areas[closest_segmented_mean_depth_idx]:
                                # NOTE: Avoid truncated zero depth values
                                if self.reference_depth_raw[y, x] > 0:
                                    segmented_area_with_depth[y, x] = self.reference_depth_im[y, x]
                                    inter_segpred_im[y, x] = 255
                            

                            if show_only_first_valid_localization_result:

                                for_display = []
                                # column-1
                                for_display.append(cat_cropped_depth)
                                h, w = cat_cropped_depth.shape

                                x1, y1, x2, y2 = lookup_region
                                
                                y, x = zip(*inter)
                                black_color = (0, 0, 0)
                                cv2.putText(inter_segpred_im, str(j), (int(np.median(x))-4, int(np.median(y))), 1, 1, black_color, 1, cv2.LINE_AA)
                                seg_cropped_im = inter_segpred_im[y1:y2+1, x1:x2+1]
                                seg_cropped_im = cv2.resize(seg_cropped_im, (w, h))
                                # column-2
                                for_display.append(seg_cropped_im)

                                seg_depth_im = copy.deepcopy(segmented_area_with_depth[y1:y2+1, x1:x2+1])
                                seg_depth_im = cv2.resize(seg_depth_im, (w, h))
                                # column-3
                                for_display.append(seg_depth_im)
                                for_display_v.append(np.hstack(for_display))

                                if whether_cat_contacts:
                                    for_display_contacts.append(np.hstack(for_display))

                                first_valid_closest_mask = closest_mask_idx

                self.draw_white_rect_on_img(display_in_bbox_XYXY, segpred_display)

                for i, contact_cls in enumerate(contact_classes):
                    if cls_id not in nearby_classes:
                        nearby_classes[cls_id] = set()
                    
                    nearby_classes[cls_id].add(self.id2name(contact_cls))

                pets_contact_classes.append(contact_classes)

            self.draw_white_rect_on_img(display_in_bbox_XYXY, depth_display)

        return pets_contact_classes, depth_display, segpred_display, \
            np.vstack(for_display_contacts) if len(for_display_contacts) >= 1 else None, \
            for_display_v[first_valid_closest_mask] if len(for_display_v) >= 1 and first_valid_closest_mask != -1 else None, \
            nearby_classes, \
            cat_coords_list, cat_depth_raw_mean_list, cls_ids_list