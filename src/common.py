import bpy
import os

def import_model(in_file_path):
    """ Import model based on extension """
    ext = in_file_path.lower().split('.')[-1]

    if ext == 'obj':
        bpy.ops.wm.obj_import(filepath=in_file_path, forward_axis='NEGATIVE_Z', up_axis='Y')
    if ext == "glb":
        bpy.ops.import_scene.gltf(filepath=in_file_path)

        meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        
        if len(meshes) > 1:
            for obj in meshes:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = meshes[0]

            bpy.ops.object.join()
        return meshes[0]
        


def export_model(obj, out_file_path):

    # Select only one object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    ext = out_file_path.lower().split('.')[-1]
        
    if ext.upper() == 'OBJ':
        bpy.ops.wm.obj_export(filepath=out_file_path, export_materials=True, path_mode='COPY', forward_axis='Y', up_axis='Z', export_selected_objects=True, export_normals=False  )
    elif ext.upper() == "GLB":
        bpy.ops.export_scene.gltf(filepath=out_file_path, export_format='GLB', export_yup=True, use_selection=True)

def export_model_in_dir(obj, name, export_dir, export_format='OBJ', clear=True):
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Select only one object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    out_file_path = os.path.join(export_dir, f"{name}.{export_format.lower()}")
        
    if export_format.upper() == 'OBJ':
        bpy.ops.wm.obj_export(filepath=out_file_path, export_materials=True, path_mode='COPY', forward_axis='Y', up_axis='Z', export_selected_objects=True, export_normals=False  )
    elif export_format.upper() == "GLB":
        bpy.ops.export_scene.gltf(filepath=out_file_path, export_format='GLB', export_yup=True, use_selection=True)
    
    if clear:
        bpy.data.objects.remove(obj, do_unlink=True)


if __name__ == "__main__":
    
    import sys
    bpy.app.debug = False
    bpy.app.debug_value = 0

    folder_path = '../konkurs/mury/CE/'
    print(os.getcwd())
    for filename in os.listdir(folder_path):
        if filename.endswith(".glb"):
            child_path = os.path.join(folder_path, filename)
            print(child_path)
            child_model = import_model(child_path)
            export_model_in_dir(child_model, filename.split(".")[0] ,"../konkurs/mury/blender",'GLB')