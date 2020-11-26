import os
import yaml
import numpy as np

import open3d

#import sys
#sys.path.append(os.path.dirname(__file__))
#os.environ["PATH"] += os.pathsep + os.path.dirname(__file__)
#import pdb; pdb.set_trace()

class CatMeshLoader():

    def __init__(self, obj_config_file='obj_path.yaml'):

        if not os.path.exists(obj_config_file):
            raise ValueError("obj config file={%s} does not exist" % obj_config_file)

        self.cat_mesh_file_path = {}
        with open(obj_config_file) as f:  
            out = yaml.load(f)
            for class_id, obj_path in zip(out['CatModels']['obj_class_id'], out['CatModels']['obj_path']):
                self.cat_mesh_file_path[class_id] = os.path.join(os.path.dirname(__file__), obj_path)

    def load(self):

        cat_mesh_orig = {}
        cat_class_ids = self.cat_mesh_file_path.keys()

        for cls_id in cat_class_ids:
            # load triangle mesh from file
            cat_mesh_orig[cls_id] = open3d.io.read_triangle_mesh(self.cat_mesh_file_path[cls_id])
            if cls_id == 0:
                cat_mesh_orig[cls_id].scale(0.1, center=cat_mesh_orig[cls_id].get_center())
                cat_mesh_orig[cls_id] = cat_mesh_orig[cls_id].rotate(cat_mesh_orig[cls_id].get_rotation_matrix_from_xyz((-np.pi/2,0,0)), center=cat_mesh_orig[cls_id].get_center())
            elif cls_id == 1:
                cat_mesh_orig[cls_id].scale(1.8, center=cat_mesh_orig[cls_id].get_center())
            else:
                cat_mesh_orig[cls_id].scale(2.0, center=cat_mesh_orig[cls_id].get_center())

            if cls_id == 3:
                cat_mesh_orig[cls_id] = cat_mesh_orig[cls_id].rotate(cat_mesh_orig[cls_id].get_rotation_matrix_from_xyz((0,-np.pi,0)), center=cat_mesh_orig[cls_id].get_center())

        return cat_mesh_orig
