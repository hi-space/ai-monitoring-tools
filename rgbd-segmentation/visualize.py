import argparse
import open3d as o3d
import numpy as np
import cv2
from matplotlib import pyplot as plt


color_image_path = ""
depth_image_path = ""


def create_rgbd(color_image_path, depth_image_path, depth_scale=1000.0, depth_trunc=3.0):
    color_raw = o3d.io.read_image(color_image_path)
    depth_raw = o3d.io.read_image(depth_image_path)
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
                                                    color_raw,
                                                    depth_raw,
                                                    depth_scale=depth_scale,
                                                    depth_trunc=depth_trunc,
                                                    convert_rgb_to_intensity=False)
    return rgbd_image

def show_point_cloud(rgbd_image):
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
            rgbd_image,
            o3d.camera.PinholeCameraIntrinsic(
                o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault))

    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="visualize to point cloud")
    parser.add_argument('--rgb', help='rgb image path', default='')
    parser.add_argument('--depth', help='depth image path', default='')
    args = parser.parse_args()
    
    rgbd_image = create_rgbd(args.rgb, args.depth)
    show_point_cloud(rgbd_image)