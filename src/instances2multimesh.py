import bpy
from bpy_extras.io_utils import axis_conversion
import mathutils
import math
from godot_parser import GDScene, Node, GDObject
import sys
import os

src_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(src_dir)

import blender_utils
import utils

def convert():

    depsgraph = bpy.context.evaluated_depsgraph_get()

    instances = []
    instance_count = 0

    instance_objects = []

    for obj in bpy.data.objects:

        eval_obj = obj.evaluated_get(depsgraph)

        if len(depsgraph.object_instances) > 0:

            for inst_id, inst in enumerate(depsgraph.object_instances):
                inst_obj = inst.instance_object
                print(inst_obj)
                if not inst_obj in instance_objects:
                    instance_objects += [inst_obj]

                if inst.is_instance and inst.parent == eval_obj:
                    
                    instance_count += 1

                    world_mat = inst.matrix_world.copy()
                    print("world_mat")
                    print(world_mat)

                    rotation_quat = world_mat.to_quaternion()
                    print("rotation_quat", rotation_quat)
                    rotation = world_mat.to_euler()
                    print("rotation", list(rotation))
                    location = world_mat.to_translation()
                    print("location", list(location))
                    scale = world_mat.to_scale()
                    print("scale", list(scale))


                    # mrot_x = utils.rotate_x_matrix(-rotation[0])
                    # mrot_y = utils.rotate_y_matrix(rotation[2])
                    # mrot_z = utils.rotate_z_matrix(-rotation[1])

                    # mrot = utils.rotation_matrix(mrot_x, mrot_z, mrot_y)

                    
                    # mrot = mathutils.Matrix.Rotation(rotation[0], 4, (1, 0, 0)) @ mathutils.Matrix.Rotation(-rotation[1], 4, (0, 0, 1)) @ mathutils.Matrix.Rotation(rotation[2], 4, (0, 1, 0))
                    mrot = mathutils.Matrix.LocRotScale(mathutils.Vector((0, 0, 0)), mathutils.Euler((rotation[0], rotation[2], -rotation[1]), 'XZY').to_quaternion(), mathutils.Vector((scale[0], scale[2], scale[1])))

                    mloc = utils.translation_matrix(location[2], location[0], -location[1])
                    
                    mscale = utils.scale_matrix(scale[2], scale[0], scale[1])

                    yup_mat4 = mloc @ utils.calc_matrix(mrot, mloc, mscale)
                    yup_mat_list = utils.mat4_to_list(yup_mat4)
                    print("yup_list", yup_mat_list)

                    yup_mat_str_list = utils.list_to_string_list(yup_mat_list)
                    yup_string = utils.matrix_string_list_to_string(yup_mat_str_list)

                    instances += [yup_string]

                    
    for obj in instance_objects:
        if obj:
            blender_utils.export_mesh_as_obj(obj)

    instances_buffer = instances
    instances_buffer_str = ",".join(instances_buffer)

    # make project directories
    godot_dirs = utils.create_godot_directories()

    # export blender scene
    blender_utils.apply_instances()
    blender_utils.export_scene_as_gltf(f"{godot_dirs[3]}\\blender_scene.gltf")

    # Construct a Godot Scene file (.tscn)
    scene = GDScene()
    packed_float_array = GDObject("PackedFloat32Array", *[float(x) for x in instances_buffer_str.split(',')])
    cube_mesh = scene.add_sub_resource("BoxMesh")
    obj_mesh = scene.add_ext_resource(path=f"res://{godot_dirs[0].basename()}\\{instance_objects[0].name}.obj", type="ArrayMesh")

    # obj_ext_res_ids = []
    # obj_ext_res_refs = []
    # for obj in instance_objects:
    #     if obj:
    #         obj_ext_res = scene.add_ext_resource(path=f"res://{godot_dirs[0].basename()}\\{obj.name}.obj", type="ArrayMesh")
    #         obj_ext_id = obj_ext_res.id

    #         obj_ext_res_ids += [obj_ext_id]
    #         obj_ext_res_refs += [obj_ext_res.reference]

    multimesh = scene.add_sub_resource("MultiMesh", transform_format = 1, mesh = obj_mesh.reference, instance_count = instance_count, buffer = packed_float_array)
    instanced_blender_scene = scene.add_ext_resource(f"res://{godot_dirs[3].basename()}\\blender_scene.gltf", "PackedScene")
    with scene.use_tree() as tree:
        tree.root = Node("Main", type="Node3D")
        tree.root.add_child(
            Node(
                f"{instance_objects[1].name}'s",
                type="MultiMeshInstance3D",
                properties={"multimesh": multimesh.reference},
            )
        )
        tree.root.add_child(
            Node(
                "Blender Scene",
                instance=instanced_blender_scene.id,
            )
        )
    # Write out Scene file (.tscn)
    scene.write(f"{godot_dirs[3]}\\Multimeshes.tscn")

convert()