import os, sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from tileset_hierarchy import hierarchical_tiling, add_root
from Bbox import Bbox
from common import import_model




if __name__ == "__main__":
    TILESET_DIR = "./v2/citywalls/"
    ROOT_URI = "LOD_0.glb"

    TRANSFORM = [-0.5359511808412922,0.8442489749800153,-5.5511151231257334e-17,0,-0.48132577585309216,-0.30555810617824236,0.8215593351962873,0,0.6936006266247354,0.4403156958296417,0.5701230207172975,0,4428723.956849183,2811469.0152269676,3615934.9153855806,1]
    
    # Init tileset and create root
    root_uri = os.path.join(TILESET_DIR, ROOT_URI)
    root_model = import_model(root_uri)

    tileset = {  "asset": { "version": "1.1" }  } ## add header
    root_bbox = Bbox(root_model)
    add_root(tileset, root_bbox.getCesiumBoundingVolumeBox(), 30, TRANSFORM, ROOT_URI)
    tileset["root"]["children"] = []
    

    tileseth_path = os.path.join(TILESET_DIR, "tileset.json")
    with open(tileseth_path, "w", encoding="utf-8") as f:
        json.dump(tileset, f, indent=2)
