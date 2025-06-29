import os, sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from tileset_hierarchy import hierarchical_tiling, add_root
from Bbox import Bbox
from common import import_model

import logging
logger = logging.getLogger(__name__)





if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    TILESET_DIR = "./test/tilesets/homes/"
    ROOT_URI = "tiles/0/LOD0_0.glb"
    
    TRANSFORM = [-0.5359511808412922,0.8442489749800153,-5.5511151231257334e-17,0,-0.48132577585309216,-0.30555810617824236,0.8215593351962873,0,0.6936006266247354,0.4403156958296417,0.5701230207172975,0,4428723.956849183,2811469.0152269676,3615934.9153855806,1]

    
    root_uri = os.path.join(TILESET_DIR, ROOT_URI)
    root_model = import_model(root_uri)

    # Init tileset and create root
    tileset = {  "asset": { "version": "1.1" }  } ## add header
    root_bbox = Bbox(root_model)
    add_root(tileset, root_bbox.getCesiumBoundingVolumeBox(), 30, TRANSFORM, ROOT_URI)
    tileset["root"]["children"] = [] # prepare array for children
    
    # Geometrical tiling Low LOD models (root) at 3 levels, then assign Medium and High LOD models
    tiles_l3 = hierarchical_tiling(
        tileset_json=tileset, 
        tiles_out_dir=f'{TILESET_DIR}/tiles/',
        low_lod_path=root_uri, 
        medium_lod_dir=f'{TILESET_DIR}/tiles/4',
        high_lod_dir=f'{TILESET_DIR}/tiles/5',
    )

    tileseth_path = os.path.join(TILESET_DIR, "tileset.json")
    with open(tileseth_path, "w", encoding="utf-8") as f:
        json.dump(tileset, f, indent=2)
