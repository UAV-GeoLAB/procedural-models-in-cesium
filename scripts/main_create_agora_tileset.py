import os, sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


from tile_node import TileNode
from Bbox import Bbox
from common import import_model
from tileset_hierarchy import hierarchical_tiling, add_root, add_children




if __name__ == "__main__":
    TILESET_DIR = "./test/tilesets/agora/"
    ROOT_URI = "tiles/0/agora_0.glb"
    TRANSFORM = [-0.5359511808412922,0.8442489749800153,-5.5511151231257334e-17,0,-0.48132577585309216,-0.30555810617824236,0.8215593351962873,0,0.6936006266247354,0.4403156958296417,0.5701230207172975,0,4428723.956849183,2811469.0152269676,3615934.9153855806,1]

    MEDIUM_LOD_DIR = "./test/agora/tiles/1"
    HIGH_LOD_DIR = "./test/agora/tiles/2"

    # Init tileset and create root
    root_uri = os.path.join(TILESET_DIR, ROOT_URI)
    print(root_uri)
    root_model = import_model(root_uri)

    tileset = {  "asset": { "version": "1.1" }  } ## add header
    root_bbox = Bbox(root_model)
    add_root(tileset, root_bbox.getCesiumBoundingVolumeBox(), 5, TRANSFORM, ROOT_URI)
    tileset["root"]["children"] = []

    root_node = TileNode(name="root")
    for filename in os.listdir(MEDIUM_LOD_DIR ):
        if filename.endswith(".glb"):
            child_path = os.path.join(MEDIUM_LOD_DIR, filename)
            child_model = import_model(child_path)
            child_bbox = Bbox(child_model)
            lvl1_node = TileNode(name=f"tiles/1/{filename}", data=child_model)
            root_node.add_child(lvl1_node)
            child = add_children(tileset["root"]["children"], child_bbox.getCesiumBoundingVolumeBox(), 2, lvl1_node.name)
            high_lod_path = f"tiles/2/{filename}"
            add_children(child["children"], child_bbox.getCesiumBoundingVolumeBox(), 0.5, HIGH_LOD_DIR)
            print(child)



    tileseth_path = os.path.join(TILESET_DIR, "tileset.json")
    with open(tileseth_path, "w", encoding="utf-8") as f:
        json.dump(tileset, f, indent=2)
