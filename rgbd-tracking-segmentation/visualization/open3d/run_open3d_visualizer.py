#!/usr/bin/env python3
"""
    Requirements:
       - open3d==0.10.0 (you need GLIBC-2.27)
"""

import os
import time 
import copy

import cv2
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
from PIL import Image

from subscriber import RedisSubscriber
from visualization.open3d import vis_misc, cat_mesh_loader
from visualization.open3d.cat_mesh_loader import CatMeshLoader

import argparse

GLFW_KEY_V  = 86
PCD_SCALE = 1.0
VOXEL_SIZE = 0.01
plane_nvec_x_z_delta = 1.0
plane_nvec_y_limit = 0.9
ZOOM_SCALE = 1.8
   
class Open3DVisualizer:

    def __init__(self, args):

        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window(window_name='BeamMice', width=1000, height=1000, left=1000, top=100)
        self.vis.get_render_option().background_color = np.asarray([0, 0, 0]) # black background

    def __enter__(self):
        cat_mesh_loader = CatMeshLoader(args.cat_mesh_config)
        self.cat_mesh_orig = cat_mesh_loader.load()

        self.redis_subscribe_3d_visualizer = RedisSubscriber(args.vis_topic)

        return self 

    def __exit__(self, exception_type, exception_value, traceback):
        self.vis.destroy_window()

    def update_pcd(self, geometries, geometry_name, pcd):
        if geometry_name in geometries:
            # import pdb; pdb.set_trace()
            geometries[geometry_name].points = pcd.points
            geometries[geometry_name].colors = pcd.colors
        else:
            geometries[geometry_name] = pcd

    def run_loop(self):

        geometries = {}
        added_geometries = {}

        prev_rot_matrix = {}
        seg_im_save = None
        prev_cat_mesh_names = []
        prev_bbox_names = []

        e = True

        idx = 0
        while e:
            e = self.vis.poll_events()

            self.vis.update_renderer()

            info = self.redis_subscribe_3d_visualizer.redis_recv_pyobj(blocking=False)
            if info is None:
                continue

            loop_start = time.time()

            rgb_im = info["rgb"]
            depth_im = info["d"]
            seg_im = info["seg"]
            cat_coords_list = info["cat_coords_list"]
            depth_raw_mean_list = info["depth_raw_mean_list"]
            cls_ids_list = info['cls_ids_list']

            # rgb_im = Image.fromarray(rgb_im)
            # depth_im = Image.fromarray(depth_im)

            if seg_im is not None:
                seg_im_save = seg_im
            else:
                seg_im = seg_im_save

            rgb_im = cv2.cvtColor(rgb_im, cv2.COLOR_BGR2RGB)
            rgb_im = o3d.geometry.Image(rgb_im)
            depth_im = o3d.geometry.Image(depth_im)

            rgbd_im = o3d.geometry.RGBDImage.create_from_color_and_depth(rgb_im, depth_im, convert_rgb_to_intensity=False, depth_scale=vis_misc._PCL_SCALING_FACTOR)
            intrinsic = o3d.camera.PinholeCameraIntrinsic(width=640, height=480, cx=vis_misc._PCL_CENTER_X,cy=vis_misc._PCL_CENTER_Y,fx=vis_misc._PCL_FOCAL_LENGTH,fy=vis_misc._PCL_FOCAL_LENGTH)

            pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_im, intrinsic)

            # downpcd = pcd
            downpcd = pcd.voxel_down_sample(voxel_size=VOXEL_SIZE)
            cl, ind = downpcd.remove_statistical_outlier(nb_neighbors=10, std_ratio=2.0)
            downpcd = downpcd.select_by_index(ind)
            flip_transform = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]

            # outlier_cloud = pcd.select_down_sample(inliers, invert=True)
            downpcd.transform(flip_transform)
            self.update_pcd(geometries, 'downpcd', downpcd)

            # TODO: Fix runtime error
            # RuntimeError: [Open3D ERROR] There must be at least 'ransac_n' points.
            try:
                plane_model, inliers = downpcd.segment_plane(distance_threshold=0.01, ransac_n=100, num_iterations=1000)
            except:
                continue

            [a, b, c, d] = plane_model
            if not (-plane_nvec_x_z_delta < a < plane_nvec_x_z_delta and -plane_nvec_x_z_delta < c < plane_nvec_x_z_delta and b > plane_nvec_y_limit):
                # errect the model
                (a, b, c) = (0, 1, 0)
            
            inlier_cloud = downpcd.select_by_index(inliers)
            # inlier_cloud.paint_uniform_color([1, 0.706, 0]) # yellow color
            self.update_pcd(geometries, 'inlier_cloud', inlier_cloud)

            #if 'mesh_frame3' not in geometries:
            #    mesh_frame3 = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.01, origin=inlier_cloud.get_center())
            #    geometries['mesh_frame3'] = mesh_frame3
            #else:
            #    mesh_frame3 = geometries['mesh_frame3']
            #    mesh_frame3.translate(-mesh_frame3.get_center() + inlier_cloud.get_center())

            if len(cat_coords_list) > 0 and len(depth_raw_mean_list) > 0 and len(cls_ids_list) > 0:
                cur_cat_mesh_names = []
                cur_bbox_names = []
                for i, (cat_coord, depth_raw_mean, cls_id) in enumerate(zip(cat_coords_list, depth_raw_mean_list, cls_ids_list)):

                    cat_mesh_name = 'cat_mesh_cls-%d' % cls_id
                    bbox_name = 'oriented_bounding_bbox_cls-%d' % cls_id
                    cur_cat_mesh_names.append(cat_mesh_name)
                    cur_bbox_names.append(bbox_name)

                    x = int(cat_coord[0])
                    y = int(cat_coord[1])
                    depth = depth_raw_mean
                    cat_coord = np.asarray(vis_misc.get_coordinate(x, y, depth)) 
                    #cat_coord[0] *= scale_param
                    cat_coord[1] *= -1
                    cat_coord[2] *= -1

                    if cat_mesh_name not in geometries:
                        cat_mesh = copy.deepcopy(self.cat_mesh_orig[cls_id])
                        cat_mesh.scale(0.1, center=cat_mesh.get_center())
                        geometries[cat_mesh_name] = cat_mesh
                    else:
                        cat_mesh = geometries[cat_mesh_name]
                        if len(cat_mesh.triangles) == 0:
                            cat_mesh = copy.deepcopy(self.cat_mesh_orig[cls_id])
                            cat_mesh.scale(0.1, center=cat_mesh.get_center())
                            geometries[cat_mesh_name].triangles = cat_mesh.triangles
                            geometries[cat_mesh_name].vertices = cat_mesh.vertices
                            cat_mesh = geometries[cat_mesh_name]
                        else:
                            if prev_rot_matrix[cat_mesh_name] is not None:
                                cat_mesh.rotate(prev_rot_matrix[cat_mesh_name], center=cat_mesh.get_center())

                    cat_mesh.translate(-cat_mesh.get_center() + cat_coord)
                    if (a, b, c) != (0, 1, 0):
                        rot_matrix = vis_misc.get_rotation_matrix_to_align_a_to_b([0, 1, 0], [a, b, c])
                        cat_mesh.rotate(rot_matrix, center=cat_mesh.get_center())
                
                    """
                    if bbox_name not in geometries:
                        #oriented_bounding_bbox = cat_mesh.get_oriented_bounding_box()
                        #oriented_bounding_bbox.color = (0, 1, 0)
                        #geometries[bbox_name] = oriented_bounding_bbox
                        axis_aligned_bbox = cat_mesh.get_axis_aligned_bounding_box()
                        axis_aligned_bbox.color = (0, 1, 0)
                        geometries[bbox_name] = axis_aligned_bbox
                    else:
                        #oriented_bounding_bbox = geometries[bbox_name]
                        #oriented_bounding_bbox.rotate(prev_rot_matrix[cat_mesh_name], center=True)
                        #oriented_bounding_bbox.translate(-oriented_bounding_bbox.get_center() + cat_mesh.get_center())
                        #oriented_bounding_bbox.rotate(rot_matrix, center=True)
                        axis_aligned_bbox = cat_mesh.get_axis_aligned_bounding_box()
                        axis_aligned_bbox.color = (0, 1, 0)
                        vis.remove_geometry(geometries[bbox_name])
                        geometries[bbox_name] = axis_aligned_bbox
                        vis.add_geometry(geometries[bbox_name])
                        #geometries[bbox_name].clear()
                        #print(np.asarray(geometries[bbox_name].get_box_points()))
                        #import pdb; pdb.set_trace()
                        #geometries[bbox_name] = geometries[bbox_name].create_from_points(axis_aligned_bbox.get_box_points())
                        #print(np.asarray(geometries[bbox_name].get_box_points()))
                    """

                    if (a, b, c) != (0, 1, 0):
                        prev_rot_matrix[cat_mesh_name] = vis_misc.get_rotation_matrix_to_align_a_to_b([a, b, c], [0, 1, 0])
                    else:
                        prev_rot_matrix[cat_mesh_name] = None
                    
                    """
                    if view_toggle[0]:
                        if 'cat_mesh_frame' not in geometries:
                            cat_mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=3.0, origin=cat_mesh.get_center())
                            geometries['cat_mesh_frame'] = cat_mesh_frame
                        else:
                            cat_mesh_frame = geometries['cat_mesh_frame']
                            cat_mesh_frame.translate(-cat_mesh_frame.get_center() + cat_mesh.get_center())

                        # geometries['cat_mesh_frame'] = cat_mesh_frame
                    else:
                        if 'cat_mesh_frame' in geometries:
                            triangles_n = len(geometries['cat_mesh_frame'].triangles)
                            vertices_n = len(geometries['cat_mesh_frame'].vertices)
                            print(triangles_n, vertices_n)
                            geometries['cat_mesh_frame'].remove_triangles_by_index(range(triangles_n))
                            geometries['cat_mesh_frame'].remove_vertices_by_index(range(vertices_n))
                    """
                for cat_mesh_name in prev_cat_mesh_names:
                    if cat_mesh_name not in cur_cat_mesh_names:
                        if cat_mesh_name in geometries:
                            triangles_n = len(geometries[cat_mesh_name].triangles)
                            vertices_n = len(geometries[cat_mesh_name].vertices)
                            geometries[cat_mesh_name].remove_triangles_by_index(range(triangles_n))
                            geometries[cat_mesh_name].remove_vertices_by_index(range(vertices_n))

                for bbox_name in prev_bbox_names:
                    if bbox_name not in cur_bbox_names:
                        if bbox_name in geometries:
                            #vis.remove_geometry(geometries[bbox_name])
                            #del added_geometries[bbox_name]
                            geometries[bbox_name].translate([100, 100, 100]) # send it to far-away place

                prev_cat_mesh_names = cur_cat_mesh_names
                prev_bbox_names = cur_bbox_names
            else:
                for bbox_name in prev_bbox_names:
                    if bbox_name in geometries:
                        geometries[bbox_name].translate([100, 100, 100]) # send it to far-away place
                        #vis.remove_geometry(geometries[bbox_name])
                        # del added_geometries[bbox_name]

                for cat_mesh_name in prev_cat_mesh_names:
                    if cat_mesh_name in geometries:
                        triangles_n = len(geometries[cat_mesh_name].triangles)
                        vertices_n = len(geometries[cat_mesh_name].vertices)
                        geometries[cat_mesh_name].remove_triangles_by_index(range(triangles_n))
                        geometries[cat_mesh_name].remove_vertices_by_index(range(vertices_n))


            for (geo_name, mesh) in geometries.items():
                if geo_name not in added_geometries:
                    self.vis.add_geometry(mesh)
                    added_geometries[geo_name] = True
                else:
                    self.vis.update_geometry(mesh)

            idx += 1

            loop_duration = time.time() - loop_start

            ctr = self.vis.get_view_control()
            ctr.set_lookat([[0.0], [0.0], [-2.0]])
            # ctr.set_zoom(ZOOM_SCALE)

            self.vis.update_renderer()


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("--cat_mesh_config", type=str, default="./visualization/open3d/obj_path.yaml")
    parser.add_argument("--vis_topic", type=str, default="3d-vis")

    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()

    with Open3DVisualizer(args) as visualizer:
        visualizer.run_loop()