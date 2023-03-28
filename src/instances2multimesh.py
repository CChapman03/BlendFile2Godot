import bpy
from bpy_extras.io_utils import axis_conversion
import mathutils
import math
from godot_parser import GDScene, Node
import sys

def format_float(float_var):

    """
    Formats a float value with 4 decimal places.
    """

    final_float = float("{:.4f}".format(float_var))

    return final_float

def list_to_string(arr):
    
    """Converts a list of values to a list of strings."""
    
    return [str(x) for x in arr]

def mat4_to_string(mtx):
    
    """
    Converts a matrix to a list of strings based on the rows and columns.
    Each value is formatted into a string representaion of a float with 4 decimal places.
    """

    array = []
    for row in range(3):  # Godot transform has 3 rows
        for col in range(4): # Godot transform has 4 columns
            value = str(format_float(mtx[row][col]))
            array.append(value)

    return array

def to_multimesh(rotation_quat, rotation, location, scale):
    
    """ 
    Uses the rotation, location and scale of an instance and constucts a world matrix (blender format). 
    Then it takes the world matrix and converts it to Godot's tranformation format (Y Up).
    Finally, the converted (Godot) matrix is outputted as a list of strings.
    """

    transform_array = []
        
    quat_x = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(90.0))
    quat_y = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))
    quat_z = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(90.0))
    quat_a = rotation_quat.copy()
    quat_a.rotate(quat_x)
    quat_a.rotate(quat_y)
    quat_a.rotate(quat_z)
    quat_a.normalize()
    rot_tmp = quat_a[1]
    quat_a[1] = quat_a[3]
    quat_a[3] = rot_tmp

    rot = rotation_quat.copy() # quat_a
    loc = location.copy()
    scl = scale.copy()

    mat_sca_x = mathutils.Matrix.Scale(scl[0], 4, (1.0, 0.0, 0.0))
    mat_sca_y = mathutils.Matrix.Scale(scl[1], 4, (0.0, 1.0, 0.0))
    mat_sca_z = mathutils.Matrix.Scale(scl[2], 4, (0.0, 0.0, 1.0))

    mat_rot = rot.to_matrix()
    mat_trs = mathutils.Matrix.Translation(loc)

    mat = mathutils.Matrix(mat_trs @ mat_rot.to_4x4() @ mat_sca_x @ mat_sca_y @ mat_sca_z)
    conv_mat = axis_conversion(from_forward="Y", from_up="Z", to_forward="-Z", to_up="Y")

    print("world_mat", mat.to_4x4())

    # transform world matrix into Y-Up
    mat4 = conv_mat.to_4x4() @ mat.to_4x4()
    print("world_mat_conv", mat4)

    transform_array += mat4_to_string(mat4)
    print("transform_array", transform_array)

    return ','.join(transform_array)

def format_list_of_floats(list_of_floats):

    """
    Formats a list of floats so that each element has 4 decimal places.
    """

    formated_list = []
    for x in list_of_floats:
        formated_list += [float("{:.4f}".format(x))]

    return formated_list

def convert():

    depsgraph = bpy.context.evaluated_depsgraph_get()

    instances = []
    instance_count = 0

    for obj in bpy.data.objects:

        eval_obj = obj.evaluated_get(depsgraph)

        if len(depsgraph.object_instances) > 0:

            for inst_id, inst in enumerate(depsgraph.object_instances):
                inst_obj = inst.instance_object

                if inst.is_instance and inst.parent == eval_obj:
                    
                    instance_count += 1

                    world_mat = inst.matrix_world.copy()
                    print("world_mat")
                    print(world_mat)

                    rotation_quat = world_mat.to_quaternion()
                    rotation = format_list_of_floats(world_mat.to_euler())
                    print("rotation", list(rotation))
                    location = format_list_of_floats(world_mat.to_translation())
                    print("location", list(location))
                    scale = format_list_of_floats(world_mat.to_scale())
                    print("scale", list(scale))

                    instances += [to_multimesh(rotation_quat, rotation, location, scale)]

                    
    instances_buffer = instances
    instances_buffer_str = ",".join(instances_buffer).replace("[", "").replace("]", "")

    # Construct a Godot Scene file (.tscn)
    scene = GDScene()
    cube_mesh = scene.add_sub_resource("BoxMesh") # TODO: Use actual instance meshes instead of only cubes!
    multimesh = scene.add_sub_resource("MultiMesh", transform_format = 1, mesh = cube_mesh.reference, instance_count = instance_count, buffer = f"PackedFloat32Array({instances_buffer_str})")
    with scene.use_tree() as tree:
        tree.root = Node("Main", type="Node3D")
        tree.root.add_child(
            Node(
                "Cubes",
                type="MultiMeshInstance3D",
                properties={"multimesh": multimesh.reference},
            )
        )
    # Write out Scene file (.tscn)
    scene.write("out\\Test_Multimesh.tscn")

    # Remove any unnescesary single or double quote literials from the .tscn file 
    in_lines = []
    with open("out\\Test_Multimesh.tscn", 'r') as file:
        for line in file.readlines():
            if "\"PackedFloat32Array" in line:
                new_line = line.replace("\"PackedFloat32Array", "PackedFloat32Array")

                if ")\"" in new_line:
                    new_line = new_line.replace(")\"", ")")

                in_lines += [new_line]
            else:
                in_lines += [line]

    with open("out\\Test_Multimesh.tscn", 'w') as file:
        file.writelines(in_lines)
