import bpy
import mathutils
import bmesh
from bpy_extras.io_utils import axis_conversion
import math
import sys
import os
from itertools import count, takewhile

def matrix_to_Y_Up(matrix):

    """
    Converts a blender Matrix into a matrix using the Y axis as the Up vector.
    """

    conv_mat = axis_conversion(from_forward="Y", from_up="Z", to_forward="-Z", to_up="Y")

    print("Original Matrix", matrix.to_4x4())

    # transform world matrix into Y-Up
    mat4 = conv_mat.to_4x4() @ matrix.to_4x4()
    print("Converted YUp Matrix", mat4)

    return mat4

def construct_matrix(rotation_quat, rotation, location, scale):
    
    """ 
    Uses the rotation, location and scale of an instance and constucts a world matrix (blender format). 
    Then it takes the world matrix and converts it to Godot's tranformation format (Y Up).
    """
        
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

    rot = quat_a # rotation_quat.copy()
    # rot.rotate(quat_x)
    # rot.rotate(quat_y)
    # rot.rotate(quat_z)
    loc = location.copy()
    scl = scale.copy()

    mat_sca_x = mathutils.Matrix.Scale(scl[0], 4, (1.0, 0.0, 0.0))
    mat_sca_y = mathutils.Matrix.Scale(scl[1], 4, (0.0, 1.0, 0.0))
    mat_sca_z = mathutils.Matrix.Scale(scl[2], 4, (0.0, 0.0, 1.0))

    mat_rot = rot.to_matrix()
    mat_trs = mathutils.Matrix.Translation(loc)

    mat = mathutils.Matrix(mat_trs @ mat_rot.to_4x4() @ mat_sca_x @ mat_sca_y @ mat_sca_z)
    conv_mat = axis_conversion(from_forward="Y", from_up="Z", to_forward="-Z", to_up="Y")

    print("Constructed Matrix", mat.to_4x4())

    # transform world matrix into Y-Up
    mat4 = conv_mat.to_4x4() @ mat.to_4x4()
    print("Constructed Matrix Converted", mat4)

    return mat4

def uv_from_active_quads(obj):
    # Toggle into Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select a single face
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    # notice in Bmesh polygons are called faces
    bm.faces[0].select = True  # select index 0
    # Show the updates in the viewport
    bmesh.update_edit_mesh(me)

    # reset face uvs
    bpy.ops.uv.reset()

    # select all faces
    bpy.ops.mesh.select_all(action='SELECT')

    # unwrap
    bpy.ops.uv.follow_active_quads()

    # select all uvs
    bpy.ops.uv.select_all(action='SELECT')

    # pack uvs
    bpy.ops.uv.pack_islands()

    # Toggle out of Edit Mode
    bpy.ops.object.mode_set(mode='OBJECT')

def uv_from_unwrap():
    # Toggle into Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select the geometry
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Unwrap
    bpy.ops.uv.unwrap()

    # Toggle out of Edit Mode
    bpy.ops.object.mode_set(mode='OBJECT')

def uv_from_cube_projection():

    # Toggle into Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select the geometry
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Unwrap
    bpy.ops.uv.cube_project(scale_to_bounds=True)

    # Toggle out of Edit Mode
    bpy.ops.object.mode_set(mode='OBJECT')

def uv_from_smart_project():

    # Toggle into Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select the geometry
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Unwrap
    bpy.ops.uv.smart_project()

    # Toggle out of Edit Mode
    bpy.ops.object.mode_set(mode='OBJECT')

def uv_from_sperate_parts(obj, sections=6):

    def frange(start, stop, step):
        return takewhile(lambda x: x< stop, count(start, step))

    # Toggle into Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Split object into many sections
    me = obj.data
    sx, sy, sz = tuple(obj.dimensions)

    bm = bmesh.from_edit_mesh(me)

    edges = []

    for i in frange(-sx / 2.0 - 0.1, sx / 2.0 + 0.1, (sx + 0.2) / float(sections)):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(i,0,0), plane_no=(-1,0,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

    for i in frange(-sy / 2.0 - 0.1, sy / 2.0 + 0.1, (sy + 0.2) / float(sections)):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,i,0), plane_no=(0,1,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

    for i in frange(-sz / 2.0 - 0.1, sz / 2.0 + 0.1, (sz + 0.2) / float(sections)):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,i,0), plane_no=(0,0,1))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

    bmesh.update_edit_mesh(me)

    bpy.ops.mesh.separate(type='LOOSE')

    # Toggle out of Edit Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # select all object parts
    bpy.ops.object.select_all(action="SELECT")

    # Get all objects in selection
    sel = bpy.context.selected_objects

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    for sub_obj in sel:
        # Select each object part
        sub_obj.select_set(True)
        
        # Make it active
        bpy.context.view_layer.objects.active = sub_obj

        # unwrap all parts:
        uv_from_unwrap()

        # Deselect the object
        obj.select_set(False)

    # select all object parts
    bpy.ops.object.select_all(action="SELECT")

    # Join all objects together
    bpy.ops.object.join()

    # deselect all
    bpy.ops.object.select_all(action="DESELECT")

    # select joined object
    bpy.ops.object.select_all(action="SELECT")

    # Toggle into Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Select the geometry
    bpy.ops.mesh.select_all(action='SELECT')

    # merge duplicate vertices
    bpy.ops.mesh.remove_doubles()

    # select all uvs
    bpy.ops.uv.select_all(action='SELECT')

    # pack uvs
    bpy.ops.uv.pack_islands()

    # Toggle out of Edit Mode
    bpy.ops.object.mode_set(mode='OBJECT')

def uv_from_sperate_part_seams(obj, sections=6):

    def frange(start, stop, step):
        return takewhile(lambda x: x< stop, count(start, step))

    # Toggle into Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Split object into many sections
    me = obj.data
    sx, sy, sz = tuple(obj.dimensions)

    bm = bmesh.from_edit_mesh(me)

    all_edges = []
    edges = []

    for i in frange(-sx / 2.0 - 0.1, sx / 2.0 + 0.1, (sx + 0.2) / float(sections)):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(i,0,0), plane_no=(-1,0,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

        all_edges += [e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]

    for i in frange(-sy / 2.0 - 0.1, sy / 2.0 + 0.1, (sy + 0.2) / float(sections)):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,i,0), plane_no=(0,1,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

        all_edges += [e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]

    for i in frange(-sz / 2.0 - 0.1, sz / 2.0 + 0.1, (sz + 0.2) / float(sections)):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,i,0), plane_no=(0,0,1))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

        all_edges += [e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]

    bmesh.update_edit_mesh(me)

    # delselect all vertices
    bpy.ops.mesh.select_all(action="DESELECT")

    # loop through cut edges
    for edge in all_edges:
        edge.select = True

    bmesh.update_edit_mesh(me)

    #bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.mesh.mark_seam(clear=False)

    # select all of mesh
    bpy.ops.mesh.select_all(action="SELECT")

    # merge duplicate vertices
    bpy.ops.mesh.remove_doubles()

    # select all object parts
    bpy.ops.mesh.select_all(action="SELECT")

    # unwrap all parts:
    bpy.ops.uv.unwrap()

    # select all uvs
    bpy.ops.uv.select_all(action='SELECT')

    # pack uvs
    bpy.ops.uv.pack_islands()

    # Toggle out of Edit Mode
    bpy.ops.object.mode_set(mode='OBJECT')

def set_active_object(obj):
    bpy.context.view_layer.objects.active = obj

def deselect_all():
    for obj in bpy.context.scene.objects:
        obj.select_set(False)

def create_collection(collection_name):
    collection_found = False
    collection_to_use = None
    
    for coll in bpy.data.collections:
        if coll.name == collection_name:
            collectionFound = True
            print(f"Collection: {collection_name} found in scene!")
            break

    if not collection_found:
        # New Collection
        new_coll = bpy.data.collections.new(collection_name)

        # Add collection to scene collection
        bpy.context.scene.collection.children.link(new_coll)

        collection_to_use = new_coll
    else:
        collection_to_use = bpy.data.collections[collection_name]

    return collection_to_use

def duplicate_object(obj):
    # deselect all objects
    deselect_all()

    # get original object's name
    obj_name = obj.name
    # create duplicated objects name 
    new_obj_name = f"{obj_name}.001"

    # create duplicated object
    new_obj = bpy.data.objects.new(new_obj_name, obj.data.copy())
    # assign new name to duplicated object
    new_obj.name = new_obj_name

    # Create a new collection called "Temp" if it doesn't already exist
    temp_coll = create_collection("Temp")
    # Add new object to "Temp" collection
    temp_coll.objects.link(new_obj)

    return new_obj

def reset_object_transforms(obj):
    # deselect all objects
    deselect_all()

    # Select object
    obj.select_set(True)

    # define matrix to reset transforms
    reset_matrix = mathutils.Matrix([[1, 0, 0, 0],
                                    [0, 1, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]])
    
    # Clear/Reset object's transformations
    obj.matrix_world = reset_matrix

    # deselect object
    obj.select_set(False)

def export_mesh_as_obj(obj):

    # Deselect all objects
    deselect_all()

    # duplicate object
    new_obj = duplicate_object(obj)

    # Select object
    new_obj.select_set(True)

    # export
    bpy.ops.wm.obj_export(filepath=f"out\\res\\3d_objects\\{obj.name}", apply_modifiers=True, export_selected_objects=True, export_triangulated_mesh=True, export_pbr_extensions=True, export_uv=True, export_normals=True, export_colors=True, export_materials=True, export_material_groups=True, export_vertex_groups=True)

    # Deselect object
    new_obj.select_set(False)

def create_blender_image(img_name, img_width, img_height):
     # Create blank image
    img = bpy.data.images.new(img_name, img_width, img_height)

    return img

def save_blender_image(img, filename):
    img.save_render(filepath=filename)

def create_material(mat_name):

    new_mat_name = mat_name
    mat = None

    for mat in bpy.data.materials:
        if mat.name == new_mat_name or mat.name_full == new_mat_name:
            new_mat_name = f"{mat_name}.0001"

    if mat is None:
        # create material
        mat = bpy.data.materials.new(name=new_mat_name)

    return mat

def get_material(mat_name):
    # Get material by name
    mat = bpy.data.materials.get(mat_name)

    return mat

def assign_material_to_object(obj, mat):

    # Assign material to object
    if obj.data.materials:
        # assign to 1st material slot
        obj.data.materials[0] = mat
    else:
        # no slots
        obj.data.materials.append(mat)

def bake_color_from_active_object():
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, save_mode='EXTERNAL')

def set_vertex_color_attribute_in_material(mat, attribute_name):
    mat.use_nodes = True #Here it is assumed that the materials have been created with nodes, otherwise it would not be possible to assign a node for the Bake, so this step is a bit useless
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    principle = nodes.get('Principled BSDF')
    attr = nodes.new("ShaderNodeAttribute")
    attr.attribute_name = attribute_name

    links.new(attr.outputs[0], principle.inputs[0])

def set_baking_material_image(mat, img):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    texture_node = bpy.data.materials[0].node_tree.nodes['Bake_node']
    texture_node.select = True
    nodes.active = texture_node
    texture_node.image = img

def add_baking_nodes_to_mat(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    texture_node = nodes.new('ShaderNodeTexImage')
    texture_node.name = 'Bake_node'
    texture_node.select = True
    nodes.active = texture_node

def bake_object_vertex_colors(obj, res=1024):

    # create a new shader material
    mat = create_material("vertex_color_bake")
    
    # Setup Vertex Color nodes
    set_vertex_color_attribute_in_material(mat, "Col")

    # Add baking nodes to material
    add_baking_nodes_to_mat(mat)
    
    # Create baking image
    img = create_blender_image(f"{obj.name}_VertexColors.png", res, res)

    # set active baking image
    set_baking_material_image(mat, img)

    # assign material to object
    assign_material_to_object(obj, mat)

    # set active object
    set_active_object(obj)

    # bake the object's color
    bake_color_from_active_object()

    # save baked image
    save_blender_image(img, f"{obj.name}_VertexColors.png")