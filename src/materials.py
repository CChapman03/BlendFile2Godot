import bpy
import sys
import os

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

    def get_all_objects_materials(self, project_directory):
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                self.get_materials_from_object(obj, project_directory)

    def get_materials_from_object(self, obj, project_directory):
        
        materials = [] 

        mesh = obj.data

        for face in mesh.polygons:

            slot = obj.material_slots[face.material_index]
            mat = slot.material

            if mat is not None and mat.use_nodes and not mat in materials:
                
                self.textures.get_textures(project_dir=project_directory)
                for texture in self.textures.textures:
                    self.tres.add_ext_resource(texture, "Texture")
                
                mat_name = mat.name
                nodes = mat.node_tree.nodes

                res_properties = {}

                for node in nodes:
                    if node.type == "BSDF_PRINCIPLED":

                        mat_diffuse = node.inputs['Base Color'].default_value
                        mat_subsurface = node.inputs['Subsurface'].default_value
                        mat_subsurface_radius = node.inputs['Subsurface Radius'].default_value
                        mat_sss_color = node.inputs['Subsurface Color'].default_value
                        mat_metal = node.inputs['Metallic'].default_value
                        mat_spec = node.inputs['Specular'].default_value
                        mat_roughness = node.inputs['Roughness'].default_value
                        mat_aniso = node.inputs['Anisotropic'].default_value
                        mat_aniso_rot = node.inputs['Anisotropic Rotation'].default_value
                        mat_cc = node.inputs['Clearcoat'].default_value
                        mat_cc_roughness = node.inputs['Clearcoat Roughness'].default_value
                        mat_ior = node.inputs['IOR'].default_value
                        mat_trans = node.inputs['Transmission'].default_value
                        mat_trans_roughness = node.inputs['Transmission Roughness'].default_value
                        mat_emission = node.inputs['Emission'].default_value
                        mat_emission_strength = node.inputs['Emission Strength'].default_value
                        mat_alpha = node.inputs['Alpha'].default_value
                        mat_alpha_cutout = mat.alpha_threshold
                        mat_normal = node.inputs['Normal'].default_value
                        mat_use_alpha_clip = mat.blend_method == "CLIP"
                        mat_normal_enabled = True
                        mat_trans_enabled = mat_trans != 0.0
                        mat_trans_color = "".join(str(x) for x in list(mat_subsurface_radius) + [1])
                        mat_emission_enabled = mat_emission_strength != 0.0
                        mat_cc_enabled = mat_cc != 0.0
                        mat_aniso_enabled = mat_aniso != 0.0
                        mat_sss_enabled = mat_subsurface != 0.0

                        res_properties["params_use_alpha_scissor"] = mat_use_alpha_clip
                        res_properties["params_alpha_scissor_threshold"] = mat_alpha_cutout
                        res_properties["metallic_specular"] = mat_spec
                        res_properties["normal_enabled"] = mat_normal_enabled
                        res_properties["normal_scale"] = (mat_normal[0] + mat_normal[1] + mat_normal[2]) / 3
                        res_properties["transmission_enabled"] = mat_trans_enabled
                        res_properties["transmission"] = f"Color( {', '.join(mat_trans_color)} )"
                        res_properties["albedo_color"] = f"Color( {', '.join(str(x) for x in list(mat_diffuse))} )"
                        res_properties["metallic"] = mat_metal
                        res_properties["roughness"] = mat_roughness
                        res_properties["emission_enabled"] = mat_emission_enabled
                        res_properties["emission"] = f"Color( {', '.join(str(x) for x in list(mat_emission))} )"
                        res_properties["emission_energy"] = mat_emission_strength
                        res_properties["emission_operator"] = 0
                        res_properties["emission_on_uv2"] = False
                        res_properties["clearcoat_enabled"] = mat_cc_enabled
                        res_properties["clearcoat"] = mat_cc
                        res_properties["clearcoat_gloss"] = mat_cc_roughness
                        res_properties["anisotropy_enabled"] = mat_aniso_enabled
                        res_properties["anisotropy"] = mat_aniso
                        res_properties["subsurf_scatter_enabled"] = mat_sss_enabled
                        res_properties["subsurf_scatter_strength"] = mat_subsurface

                self.tres.add_resource(mat_name, res_properties)
                self.tres.write(f"{project_directory}/{obj.name}_{mat_name}.tres")

                materials += [mat]
                break