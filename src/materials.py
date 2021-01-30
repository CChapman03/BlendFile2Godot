import bpy
import sys
import os
import shutil

sys.path.append(os.getcwd())

from tres import TRES
from textures import Textures

class Material():

    def __init__(self):

        self.tres = TRES()
        self.textures = Textures()

        self.base_color = (1.0, 1.0, 1.0, 1.0)
        self.subsurface = 0.0
        self.subsurface_radius = (0.0, 0.0, 0.0)
        self.subsurface_color = (1.0, 1.0, 1.0, 1.0)
        self.metallic = 0.0
        self.specular = 0.0
        self.roughness = 0.5
        self.anisotropic = 0.0
        self.anisotropic_rotation = 0.0
        self.clearcoat = 0.0
        self.clearcoat_roughness = 0.0
        self.IOR = 1.45
        self.transmission = 0.0
        self.transmission_roughness = 0.0
        self.emission = (0.0, 0.0, 0.0, 0.0)
        self.emission_strength = 1.0
        self.alpha = 1.0
        self.normal = (1.0, 1.0, 1.0)

        self.materials = [] 
        self.materials_dict = {}

    def get_all_objects_materials(self, project_directory):
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                self.get_materials_from_object(obj, project_directory)

    def get_materials_from_object(self, obj, project_directory):
        
        mat_texs = []

        mesh = obj.data

        for face in mesh.polygons:

            slot = obj.material_slots[face.material_index]
            mat = slot.material

            if mat is not None and mat.use_nodes and not mat.name in self.materials_dict:
                
                mat_name = mat.name
                nodes = mat.node_tree.nodes

                res_properties = {}

                node_dict = {}

                for node in nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        
                        # node_dict = {}
                        for node_in in node.inputs:

                            node_input_name = node_in.name

                            if len(node_in.links) > 0:

                                link = node_in.links[0]
                                connected_node = link.from_node

                                if connected_node.type == "TEX_IMAGE":

                                    node_image = connected_node.image
                                    node_image_filename = node_image.filepath_raw.replace("../", "").replace("//", "/")

                                    if node_image_filename != "":
                                        base_image_filename = os.path.basename(node_image_filename)

                                        if not base_image_filename in mat_texs:

                                            shutil.copyfile(node_image_filename, f"{project_directory}/{base_image_filename}")
                                            mat_texs += [base_image_filename]

                                        node_dict[node_input_name] = f"ExtResource( {len(mat_texs)} )"
                            
                            else:
                                node_dict[node_input_name] = node_in.default_value

                        mat_diffuse = node_dict['Base Color']
                        mat_subsurface = node_dict['Subsurface']
                        mat_subsurface_radius = node_dict['Subsurface Radius']
                        mat_sss_color = node_dict['Subsurface Color']
                        mat_metal = node_dict['Metallic']
                        mat_spec = node_dict['Specular']
                        mat_roughness = node_dict['Roughness']
                        mat_aniso = node_dict['Anisotropic']
                        mat_aniso_rot = node_dict['Anisotropic Rotation']
                        mat_cc = node_dict['Clearcoat']
                        mat_cc_roughness = node_dict['Clearcoat Roughness']
                        mat_ior = node_dict['IOR']
                        mat_trans = node_dict['Transmission']
                        mat_trans_roughness = node_dict['Transmission Roughness']
                        mat_emission = node_dict['Emission']
                        mat_emission_strength = node_dict['Emission Strength']
                        mat_alpha = node_dict['Alpha']
                        mat_alpha_cutout = mat.alpha_threshold
                        mat_normal = node_dict['Normal']

                        mat_use_alpha_clip = mat.blend_method == "CLIP"
                        mat_normal_enabled = mat_normal[0] + mat_normal[1] + mat_normal[2] != 0.0
                        mat_trans_enabled = mat_trans != 0.0
                        mat_trans_color = ", ".join(str(x) for x in [mat_subsurface_radius[0], mat_subsurface_radius[1], mat_subsurface_radius[2], 1.0])
                        mat_emission_enabled = mat_emission_strength > 0.0 and mat_emission[0] + mat_emission[1] + mat_emission[2] > 0.0 or "ExtResource" in mat_emission
                        mat_cc_enabled = mat_cc != 0.0
                        mat_aniso_enabled = mat_aniso != 0.0
                        mat_sss_enabled = mat_subsurface != 0.0
                        mat_normal_color = ', '.join(str(x) for x in [mat_normal[0], mat_normal[1], mat_normal[2], 1.0])

                        res_properties["params_use_alpha_scissor"] = str(mat_use_alpha_clip).lower()
                        res_properties["params_alpha_scissor_threshold"] = mat_alpha_cutout
                        res_properties["metallic_specular"] = mat_spec
                        res_properties["normal_enabled"] = str(mat_normal_enabled).lower()
                        res_properties["normal_scale"] = (mat_normal[0] + mat_normal[1] + mat_normal[2]) / 3 if not "ExtResource" in mat_normal else 1.0
                        res_properties["normal_texture"] = f"Color( {mat_normal_color} )" if not "ExtResource" in mat_normal else mat_normal
                        res_properties["transmission_enabled"] = str(mat_trans_enabled).lower()
                        res_properties["transmission"] = f"Color( {mat_trans_color} )" if not "ExtResource" in mat_trans_color else mat_trans_color
                        res_properties["albedo_color"] = f"Color( {', '.join(str(x) for x in list(mat_diffuse))} )" if not "ExtResource" in mat_diffuse else f"Color( 1, 1, 1, 1 )"
                        if "ExtResource" in mat_diffuse:
                            res_properties["albedo_texture"] = mat_diffuse
                        res_properties["metallic"] = mat_metal
                        res_properties["roughness"] = mat_roughness
                        res_properties["emission_enabled"] = str(mat_emission_enabled).lower()
                        res_properties["emission"] = f"Color( {', '.join(str(x) for x in list(mat_emission))} )" if not "ExtResource" in mat_emission else mat_emission
                        res_properties["emission_energy"] = mat_emission_strength
                        res_properties["emission_operator"] = 0
                        res_properties["emission_on_uv2"] = "false"
                        res_properties["clearcoat_enabled"] = str(mat_cc_enabled).lower()
                        res_properties["clearcoat"] = mat_cc
                        res_properties["clearcoat_gloss"] = mat_cc_roughness
                        res_properties["anisotropy_enabled"] = str(mat_aniso_enabled).lower()
                        res_properties["anisotropy"] = mat_aniso
                        res_properties["subsurf_scatter_enabled"] = str(mat_sss_enabled).lower()
                        res_properties["subsurf_scatter_strength"] = mat_subsurface

                self.materials_dict[mat.name] = {"Material" : res_properties, "Textures" : mat_texs, "Object" : obj.name}

        for mat_name, mat_properties in self.materials_dict.items():
            
            mat_res_properties = mat_properties["Material"]
            mat_textures = mat_properties["Textures"]

            self.tres = TRES()

            temp_textures = []
            for texture in mat_textures:

                if not os.path.basename(texture) in temp_textures:
                    self.tres.add_ext_resource(os.path.basename(texture), "Texture")

                    temp_textures += [os.path.basename(texture)]

            self.tres.add_resource(mat_name, mat_res_properties)
            self.tres.write(f"{project_directory}/{mat_name}.tres")