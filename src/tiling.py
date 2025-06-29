import bpy
import os, sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
from common import import_model, export_model_in_dir



class Bbox:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ):
        self.xmin = minX
        self.ymin = minY
        self.xmax = maxX
        self.ymax = maxY
        self.zmin = minZ
        self.zmax = maxZ

    def __str__(self):
        return f'''
            MinX: {self.xmin}\n
            MinY: {self.ymin}\n
            MaxY: {self.xmax}\n
            MaxY: {self.ymax}\n
        '''

def extract_tiles_bboxes(obj, num_along_X, num_along_Y, num_along_Z):
    min_x, min_y, min_z = [obj.matrix_world @ v.co for v in obj.data.vertices][0]
    max_x, max_y, max_z = [obj.matrix_world @ v.co for v in obj.data.vertices][0]
    for v in obj.data.vertices:
        world_co = obj.matrix_world @ v.co
        min_x, min_y, min_z = min(min_x, world_co.x), min(min_y, world_co.y), min(min_z, world_co.z)
        max_x, max_y, max_z = max(max_x, world_co.x), max(max_y, world_co.y), max(max_z, world_co.z)
    
    mesh_bbox = Bbox(min_x, min_y, min_z, max_x,max_y, max_z)

    rangeX_tile = (max_x - min_x) / num_along_X
    rangeY_tile = (max_y - min_y) / num_along_Y
    rangeZ_tile = (max_z - min_z) / num_along_Z

    tiles_bbox = []
    for ix in range(0, num_along_X):
        xmin_tile = mesh_bbox.xmin + rangeX_tile * ix
        xmax_tile = xmin_tile + rangeX_tile
        for iy in range(0, num_along_Y):
            ymin_tile = mesh_bbox.ymin + rangeY_tile * iy
            ymax_tile = ymin_tile + rangeY_tile
            for iz in range(0, num_along_Z):
                zmin_tile = mesh_bbox.zmin + rangeZ_tile * iz
                zmax_tile = zmin_tile + rangeZ_tile
                tiles_bbox.append(Bbox(xmin_tile, ymin_tile, zmin_tile, xmax_tile, ymax_tile, zmax_tile))

    return tiles_bbox




def bisect_object_by_plane(obj, axis='X', location=0.0, clear_inner=False, clear_outer=False):

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Select the whole mesh i cut it
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(
        plane_co=(location, location, location),
        plane_no=(1 if axis == 'X' else 0, 
                  1 if axis == 'Y' else 0, 
                  1 if axis == 'Z' else 0),
        clear_inner=clear_inner,
        clear_outer=clear_outer
    )

    bpy.ops.object.mode_set(mode='OBJECT')
    return obj  # 

def bisect_in_bbox(obj, minX=0.0, minY=0.0, maxX=0.0, maxY=0.0, minZ=0.0, maxZ=0.0):
    # Bisect along X axis
    clipped_obj = bisect_object_by_plane(obj, axis='X', location=minX, clear_inner=True, clear_outer=False)
    clipped_obj = bisect_object_by_plane(clipped_obj, axis='X', location=maxX, clear_inner=False, clear_outer=True)

    # Bisect along Y axis
    clipped_obj = bisect_object_by_plane(clipped_obj, axis='Y', location=minY, clear_inner=True, clear_outer=False)
    clipped_obj = bisect_object_by_plane(clipped_obj, axis='Y', location=maxY, clear_inner=False, clear_outer=True)

    # Bisect along Z axis
    clipped_obj = bisect_object_by_plane(clipped_obj, axis='Z', location=minZ, clear_inner=True, clear_outer=False)
    clipped_obj = bisect_object_by_plane(clipped_obj, axis='Z', location=maxZ, clear_inner=False, clear_outer=True)

    return clipped_obj



def duplicate_object(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.duplicate()
    return bpy.context.selected_objects[0]  # duplicate of objects



def tiling(filepath, numX, numY, numZ,  outDir, out_format):
    # file_path = bpy.path.abspath(r"../data/a.obj")  
    file_path = bpy.path.abspath(filepath)
    tiles = []
    imported_obj = import_model(file_path)
    if imported_obj:
        bboxes = extract_tiles_bboxes(imported_obj, numX,numY,numZ)
        for idx, bbox in enumerate(bboxes):
            obj = duplicate_object(imported_obj)
            tile_obj = bisect_in_bbox(obj, minX=bbox.xmin, minY=bbox.ymin, minZ= bbox.zmin, maxX=bbox.xmax, maxY=bbox.ymax, maxZ=bbox.zmax)
            tiles.append(tile_obj)
            export_model_in_dir(tile_obj, f"{idx}",outDir , out_format, clear=False)
        return tiles
    else:
        print("Model file not loaded.")

def tiling_object(imported_obj, numX, numY, numZ,  outDir, out_format):
    # file_path = bpy.path.abspath(r"../data/a.obj")  

    tiles = []
    if imported_obj:
        bboxes = extract_tiles_bboxes(imported_obj, numX,numY,numZ)
        for idx, bbox in enumerate(bboxes):
            obj = duplicate_object(imported_obj)
            tile_obj = bisect_in_bbox(obj, minX=bbox.xmin, minY=bbox.ymin, minZ= bbox.zmin, maxX=bbox.xmax, maxY=bbox.ymax, maxZ=bbox.zmax)
            tiles.append(tile_obj)
            export_model_in_dir(tile_obj, f"{idx}",outDir , out_format, clear=False)
        return tiles
    else:
        print("Model file not loaded.")

def hierarchical_tiling(filepath, tiles_dir):
    # Poziom 1 - podział na 4 części (2x2)
    parts_lvl1 = tiling(filepath, 2, 2, 1, os.path.join(tiles_dir, "1"), "GLB")
    print(parts_lvl1)

    parts_lvl2 = []
    for idx, part in enumerate(parts_lvl1):
        sub_parts = tiling_object(part, 2, 1, 1, os.path.join(tiles_dir, f"2/{idx}"), "GLB")
        parts_lvl2.extend(sub_parts)

    parts_lvl3 = []
    for idx, part in enumerate(parts_lvl2):
        sub_parts = tiling_object(part, 1, 2, 1, os.path.join(tiles_dir, f"3/{idx}"), "GLB")
        parts_lvl3.append(sub_parts)
    
    tiles_lvl3 = []
    for p in parts_lvl3:
        for tile in p:
            tiles_lvl3.append(tile)

    return tiles_lvl3

if __name__ == "__main__":
    hierarchical_tiling(filepath='../my-tileset/tiles/0/pyexport.glb', tiles_dir="../my-tileset/tiles")
    print()



    

