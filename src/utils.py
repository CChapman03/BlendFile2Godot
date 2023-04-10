import math
import bpy
import mathutils
from bpy_extras.io_utils import axis_conversion

from path import Path

def rotate_x_matrix(rotation_angle):

    angle_rad = rotation_angle

    cos = math.cos(angle_rad)
    sin = math.sin(angle_rad)

    rot_mat = mathutils.Matrix(((1.0, 0.0, 0.0, 0.0), 
                                (0.0, cos, -sin, 0.0), 
                                (0.0, sin, cos, 0.0), 
                                (0.0, 0.0, 0.0, 1.0)))
    
    return rot_mat

def rotate_y_matrix(rotation_angle):

    angle_rad = rotation_angle

    cos = math.cos(angle_rad)
    sin = math.sin(angle_rad)

    rot_mat = mathutils.Matrix(((cos, 0.0, sin, 0.0), 
                                (0.0, 1.0, 0.0, 0.0), 
                                (-sin, 0.0, cos, 0.0), 
                                (0.0, 0.0, 0.0, 1.0)))
    
    return rot_mat

def rotate_z_matrix(rotation_angle):

    angle_rad = rotation_angle

    cos = math.cos(angle_rad)
    sin = math.sin(angle_rad)

    rot_mat = mathutils.Matrix(((cos, -sin, 0.0, 0.0), 
                                (sin, cos, 0.0, 0.0), 
                                (0.0, 0.0, 1.0, 0.0), 
                                (0.0, 0.0, 0.0, 1.0)))
    
    return rot_mat

def rotation_matrix(mat_x, mat_y, mat_z):
    rot_mat = mat_x @ mat_y @ mat_z

    return rot_mat

def scale_matrix(sx, sy, sz):

    scale_mat = mathutils.Matrix(((sx, 0.0, 0.0, 0.0), 
                                (0.0, sy, 0.0, 0.0), 
                                (0.0, 0.0, sz, 0.0), 
                                (0.0, 0.0, 0.0, 1.0)))
    
    return scale_mat

def translation_matrix(x, y, z):
    translation_matrix = mathutils.Matrix(((1.0, 0.0, 0.0, x), 
                                        (0.0, 1.0, 0.0, y), 
                                        (0.0, 0.0, 1.0, z), 
                                        (0.0, 0.0, 0.0, 1.0)))
    
    return translation_matrix

def calc_matrix(mat_rot, mat_loc, mat_scale):
    mat4 =  mat_rot

    return mat4

def create_godot_directories():
    directories_to_create = ["3d_objects", "materials", "textures", "scenes", "scripts"]
    project_dir = Path("out").joinpath("Godot4_Project")

    for directory in directories_to_create:
        directory_path = project_dir.joinpath(directory)

        directory_path.mkdir_p()

    return [project_dir.joinpath(directory) for directory in directories_to_create]

def format_float(float_var):

    """
    Formats a float value with 4 decimal places.
    """

    final_float = float("{:.3f}".format(float_var))

    return final_float

def list_to_string(arr):
    
    """Converts a list of values to a list of strings."""
    
    return [str(x) for x in arr]

def matrix4x4_to_matrix3x4(matrix4x4):

    """
    Truncates a 4x4 Matrix to a 3x4 Matrix
    """

    final_matrix = mathutils.Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)))
    for row in range(3):
        for col in range(4):
            final_matrix[row][col] = matrix4x4[row][col]

    return final_matrix

def mat4_to_list(mat4):
    
    result = []

    for row in range(3):
        result += [mat4[row][0], mat4[row][1], mat4[row][2], mat4[row][3]]

    print("result", result)
    return result

def matrix4x4_to_list(matrix4x4):

    """
    Truncates a 4x4 Matrix to a 3x4 Matrix
    """

    final_matrix = mathutils.Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    for row in range(3):
        for col in range(4):
            final_matrix[row][col] = matrix4x4[row][col]

    # basis_mat = mathutils.Matrix(((matrix4x4[0][0], matrix4x4[1][0], matrix4x4[2][0], matrix4x4[3][0]), (matrix4x4[0][1], matrix4x4[1][1], matrix4x4[2][1], matrix4x4[3][1]), (matrix4x4[0][2], matrix4x4[1][2], matrix4x4[2][2], matrix4x4[3][2])))

    quat_x = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(19.0))
    quat_y = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(-25.0))
    quat_z = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(-90.0))
    basis_mat = matrix4x4.to_3x3() #matrix4x4.to_3x3()
    # basis_mat.rotate(quat_x)
    # basis_mat.rotate(quat_y)
    # basis_mat.rotate(quat_z)
    origin = [matrix4x4[0][3], matrix4x4[1][3], matrix4x4[2][3]]

    result = [basis_mat[0][0], basis_mat[0][1], basis_mat[0][2], origin[0], basis_mat[1][0], basis_mat[1][1], basis_mat[1][2], origin[1], basis_mat[2][0], basis_mat[2][1], basis_mat[2][2], origin[2]]

    return result
    #return matrix4x4.to_3x3(), [matrix4x4[0][3], matrix4x4[1][3], matrix4x4[2][3]]

def matrix4x4_to_matrix3x4_YXZ(matrix4x4):

    """
    Truncates a 4x4 Matrix to a 3x4 Matrix
    """

    final_matrix = mathutils.Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    for row in range(3):
        for col in range(4):
            final_matrix[row][col] = matrix4x4[row][col]

    # final_swapped_matrix = mathutils.Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0)))
    # # swap X with Y
    # x_axis = 1
    # y_axis = 0
    # z_axis = 2
    
    # # swap basis and origin
    # final_swapped_matrix[x_axis] = final_matrix[y_axis]
    # final_swapped_matrix[y_axis] = final_matrix[x_axis]
    # final_swapped_matrix[z_axis] = final_matrix[z_axis]

    # revert back origin
    # final_swapped_matrix[0][3] = final_matrix[0][3]
    # final_swapped_matrix[1][3] = final_matrix[1][3]
    # final_swapped_matrix[2][3] = final_matrix[2][3]

    print(final_matrix)

    conv_mat = mathutils.Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))) 
    final_swapped_matrix = conv_mat @ final_matrix

    # res_mat = mathutils.Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    # for row in range(4):
    #     for col in range(3):
    #         res_mat[row][col] = final_swapped_matrix[row][col]

    return final_swapped_matrix

def matrix4x4_to_matrix4x3(matrix4x4):

    """
    Truncates a 4x4 Matrix to a 4x3 Matrix
    """

    final_matrix = mathutils.Matrix(((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)))
    for row in range(4):
        for col in range(3):
            final_matrix[row][col] = matrix4x4[row][col]

    return final_matrix

def list_to_string_list(list):
    result = []
    for item in list:
        result += [str(format_float(item))]

    return result

def matrix_to_string_list(mtx):
    """
    Converts a matrix to a list of floats based on the rows and columns.
    Each value is formatted into a float with 4 decimal places.
    """

    rows = len(mtx)
    cols = len(mtx[0])

    array = []
    for row in range(rows):
        for col in range(cols):
            value = str(format_float(mtx[row][col]))
            array.append(value)

    return array

def matrix_string_list_to_string(mtx_str_list):
    
    """
    Converts a string list of a matrix to a string
    """

    return ','.join(mtx_str_list)