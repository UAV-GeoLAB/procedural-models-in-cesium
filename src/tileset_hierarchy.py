import bpy
import os, sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

import json
from typing import Dict, List

from Bbox import Bbox, BboxCesium
from common import import_model, export_model_in_dir
from tiling import tiling, tiling_object
from tile_node import TileNode, print_graph, iterate_dfs

bpy.app.debug = False
bpy.app.debug_value = 0

# sys.stdout = open(os.devnull, 'w')
# sys.stderr = open(os.devnull, 'w')

import logging
logger = logging.getLogger(__name__)

def add_root(json_obj, bbox, geomError, transform, uri):
    json_obj["geometricError"] = 3000
    json_obj["root"] = {
        "boundingVolume": {"box": bbox},
        "geometricError": geomError,
        "refine": "REPLACE",
        "transform": transform,
        "content": {"uri": uri}
    }
def add_children(children_array, bbox, geomError, uri):
    children_array.append(
        {
            "boundingVolume": {"box": bbox},
            "geometricError": geomError,
            "content": {"uri": uri},
            "children": []
        }
    )
    return children_array[-1]

def hierarchical_tiling(
        tileset_json: Dict, 
        low_lod_path: str,
        medium_lod_dir: str,
        high_lod_dir: str,
        tiles_out_dir: str
    ) -> None:

    root_node = TileNode(name="root")
    tiles_lvl1 =  ( tiling(low_lod_path, 2, 2, 1, os.path.join(tiles_out_dir, "1"), "GLB") )
    for i, tile1 in enumerate(tiles_lvl1):
        lvl1_node = TileNode(name=f"tiles/1/{i}.glb", data=tile1)
        root_node.add_child(lvl1_node)

        # Level 2
        tiles_lvl2 = tiling_object(tile1, 2, 1, 1, os.path.join(tiles_out_dir, f"2/{i}"), "GLB")
        for j, tile2 in enumerate(tiles_lvl2):
             lvl2_node = TileNode(name=f"tiles/2/{i}/{j}.glb", data=tile2)
             lvl1_node.add_child(lvl2_node)

             #Level3
             tiles_lvl3 = tiling_object(tile2, 1, 2, 1, os.path.join(tiles_out_dir, f"3/{i}/{j}"), "GLB")
             for k, tile3 in enumerate(tiles_lvl3):
                lvl3_node = TileNode(name=f"tiles/3/{i}/{j}/{k}.glb", data=tile3)
                lvl2_node.add_child(lvl3_node)
    iterate_dfs(root_node)
    

    last_lod = []
    for i, t1 in enumerate(root_node.children):
        add_children(tileset_json["root"]["children"], Bbox(t1.data).getCesiumBoundingVolumeBox(), 20, t1.name)
        for j, t2 in enumerate(t1.children):
            add_children(tileset_json["root"]["children"][i]["children"], Bbox(t2.data).getCesiumBoundingVolumeBox(), 10, t2.name)
            for k, t3 in enumerate(t2.children):
                add_children(tileset_json["root"]["children"][i]["children"][j]["children"], Bbox(t3.data).getCesiumBoundingVolumeBox(), 5, t3.name)
                last_lod.append(tileset_json["root"]["children"][i]["children"][j]["children"])
    
    
    cnt = 0
    for filename in os.listdir(medium_lod_dir):
        cnt += 1
        print(cnt)
        if filename.endswith(".glb"):
            medium_lod_path = os.path.join(medium_lod_dir, filename)
            child_model = import_model(medium_lod_path)
            child_bbox = Bbox(child_model)
            for l in last_lod:
                for li in l:
                    c_bbox = Bbox(li["boundingVolume"]["box"])
                    if child_bbox.is_overlapping(c_bbox):
                        # Level 4
                        child = add_children(li["children"], child_bbox.getCesiumBoundingVolumeBox(), 1, f"tiles/4/{filename}")
                        # Level 5
                        high_lod_path = os.path.join(high_lod_dir, filename) # filename for High LOD should be the same what Medium LOD
                        if os.path.isfile(high_lod_path): # Check if High LOD files exists and has the same names which Medium LOD has
                            add_children(child["children"], child_bbox.getCesiumBoundingVolumeBox(), 0.5, f"tiles/5/{filename}")
                        else:
                            logger.warning(f"High LOD model for {filename } not exists! ")

        