import bpy
import os
import sys



script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from common import import_model


class Bbox:
    def __init__(self, obj):
        if isinstance(obj, (list, tuple)) and len(obj) == 12: # CEsium Bbox
            # print("Cesium BBOX", obj)
            center_x, center_y, center_z = obj[0], obj[1], obj[2]
            half_x = abs(obj[3])
            half_y = abs(obj[7])
            half_z = abs(obj[11])
            self.xmin = center_x - half_x
            self.xmax = center_x + half_x
            self.ymin = center_y - half_y
            self.ymax = center_y + half_y
            self.zmin = center_z - half_z
            self.zmax = center_z + half_z
        elif obj and isinstance(obj.data, bpy.types.Mesh):
            # print("BBOX")
            min_x, min_y, min_z = [obj.matrix_world @ v.co for v in obj.data.vertices][0]
            max_x, max_y, max_z = [obj.matrix_world @ v.co for v in obj.data.vertices][0]
            for v in obj.data.vertices:
                world_co = obj.matrix_world @ v.co
                min_x, min_y, min_z = min(min_x, world_co.x), min(min_y, world_co.y), min(min_z, world_co.z)
                max_x, max_y, max_z = max(max_x, world_co.x), max(max_y, world_co.y), max(max_z, world_co.z)

            self.xmin = min_x
            self.ymin = min_y
            self.xmax = max_x
            self.ymax = max_y
            self.zmin = min_z
            self.zmax = max_z


    def __str__(self):
        return f'''
            MinX: {self.xmin}
            MaxX: {self.xmax}
            MinY: {self.ymin}
            MaxY: {self.ymax}
            MinZ: {self.zmin}
            MaxZ: {self.zmax}\n
        '''
    def getCesiumBoundingVolumeBox(self):
        center_x = (self.xmax + self.xmin)/2
        center_y = (self.ymax + self.ymin)/2
        center_z = (self.zmax + self.zmin)/2
        half_x = (self.xmax - self.xmin)/2
        half_y = (self.ymax - self.ymin)/2
        half_z = (self.zmax - self.zmin)/2
        return [center_x, center_y, center_z,
                half_x, 0, 0,
                0, half_y, 0,
                0, 0, half_z
        ]
    

    def is_overlapping(self, other):
       return (
            self.xmin <= other.xmax and self.xmax >= other.xmin and
            self.ymin <= other.ymax and self.ymax >= other.ymin and
            self.zmin <= other.zmax and self.zmax >= other.zmin
        )

class BboxCesium():
    def __init__(self, box):
        if not isinstance(box, (list, tuple)) or len(box) != 12:
            raise ValueError("Invalid Cesium box format. Expected a list or tuple of 12 elements.")
    
        center_x, center_y, center_z = box[0], box[1], box[2]
        half_x = abs(box[3])
        half_y = abs(box[7])
        half_z = abs(box[11])
        self.xmin = center_x - half_x
        self.xmax = center_x + half_x
        self.ymin = center_y - half_y
        self.ymax = center_y + half_y
        self.zmin = center_z - half_z
        self.zmax = center_z + half_z
    
    def is_inside(self, other):
        return all([
            other.xmin <= self.xmin <= other.xmax,
            other.xmax >= self.xmax >= other.xmin,
            other.ymin <= self.ymin <= other.ymax,
            other.ymax >= self.ymax >= other.ymin,
            other.zmin <= self.zmin <= other.zmax,
            other.zmax >= self.zmax >= other.zmin,
        ])

if __name__ == "__main__":
    print(os.getcwd())
    # obj = import_model("../LOD/LOD4/LOD4_0.obj")
    obj = import_model("../LOD2/LOD2_Block_4_78.glb")
    obj2 = import_model("../my-tileset/tiles/1/3.glb")

    mesh_bbox = Bbox(obj)
    print(mesh_bbox)
    print(Bbox(obj2))
    print(mesh_bbox.getCesiumBoundingVolumeBox())
    print(mesh_bbox.is_overlapping(Bbox(obj2)))
