import math
import mathutils

def format_float(float_var):

    """
    Formats a float value with 4 decimal places.
    """

    final_float = float("{:.4f}".format(float_var))

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
