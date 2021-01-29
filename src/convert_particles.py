import bpy
import random
import mathutils
import sys

import os

sys.path.append(os.getcwd())

from math_utilities import Math_Utilities
from tscn import TSCN

class Convert_Particles():

    def __init__(self):
        self.math = Math_Utilities()
        self.depg = bpy.context.evaluated_depsgraph_get()
        self.blend_filename = os.path.basename(bpy.data.filepath)

        self.tscn = TSCN()

        self.blend_particle_dict = {"Emitter Objects" : {}}

    def deselect_all(self):
        for obj in bpy.context.scene.objects:
            obj.select_set(False)
    
    def export_object(self, obj, project_dir):

        bpy.context.scene.collection.objects.link(obj)

        obj.select_set(True)

        mat = mathutils.Matrix( [ [1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1] ])

        obj.matrix_world = mat
        bpy.ops.export_scene.obj(filepath=f"{project_dir}/{obj.name}.obj", use_selection=True, use_triangles=True, use_normals=True)
        obj.select_set(False)

        bpy.context.scene.collection.objects.unlink(obj)

    def convert(self, project_dir):

        self.deselect_all()

        for obj in bpy.context.scene.objects:

            for modifier in obj.modifiers:
                if modifier.type == "PARTICLE_SYSTEM":

                    # Object Has Particle System
                    # Get Object properties

                    # Get Object 3D Transform
                    obj_scale = obj.scale
                    obj_location = obj.location
                    obj_rotation = obj.rotation_euler

                    obj_s = self.math.S3D(obj_scale[0], obj_scale[2], obj_scale[1])
                    obj_r = self.math.R(obj_rotation[0], obj_rotation[2], obj_rotation[1])
                    obj_t = self.math.T(obj_location[0], obj_location[2], obj_location[1])

                    obj_transform = self.math.to_str(self.math.transform(obj_r, obj_s, obj_t))

                    # Other
                    obj_name = obj.name

                    self.blend_particle_dict["Emitter Objects"][obj_name] = {"Transform" : obj_transform, "Particle Objects" : {}}

                    # Get Object Particle Systems
                    obj_particle_systems = obj.evaluated_get(self.depg).particle_systems

                    for particle_system_idx, particle_system in enumerate(obj_particle_systems):

                        # Get particle system properties
                        num_of_particles = len(particle_system.particles)
                        particle_system_name = particle_system.name
                        particle_system_settings = particle_system.settings
                        particle_system_objects_dict = {}

                        # Get Particle Objects
                        if particle_system_settings.render_type == "COLLECTION":

                            for particle_obj_idx, particle_obj in enumerate(particle_system_settings.instance_collection.objects):

                                self.export_object(particle_obj, project_dir)

                                particle_system_objects_dict[particle_system_idx + particle_obj_idx] = {"Object" : particle_obj, "Random Weight" : 1, "Scale" : particle_obj.dimensions}

                                self.blend_particle_dict["Emitter Objects"][obj_name]["Particle Objects"][particle_obj.name] = particle_system_objects_dict

                        elif particle_system_settings.render_type == "OBJECT":
                            
                            particle_obj_idx = 0
                            particle_obj = particle_system_settings.instance_object

                            self.export_object(particle_obj, project_dir)

                            particle_system_objects_dict[particle_system_idx + particle_obj_idx] = {"Object" : particle_obj, "Random Weight" : 1, "Scale" : particle_obj.dimensions}

                            self.blend_particle_dict["Emitter Objects"][obj_name]["Particle Objects"][particle_obj.name] = particle_system_objects_dict

                        particle_indices = []
                        particle_index_weights = []

                        for key, val in particle_system_objects_dict.items():

                            self.tscn.add_ext_resource(f"{val['Object'].name}.obj", "ArrayMesh")

                            particle_indices += [key]
                            particle_index_weights += [val['Random Weight']]

                        
                        particle_transforms_dict = {}
                        # Loop Through all Particles
                        for particle in particle_system.particles:

                            particle_obj_id = random.choices(particle_indices, weights=particle_index_weights, k=1)[0]

                            particle_obj = particle_system_objects_dict[particle_obj_id]
                            particle_obj_scale = particle_obj['Scale']

                            particle_loc = particle.location
                            particle_rot = particle.rotation.to_euler()

                            particle_r = self.math.Ry(particle_rot[2])
                            particle_s = self.math.S3D(particle.size * particle_obj_scale[0],
                                                       particle.size * particle_obj_scale[2],
                                                       particle.size * particle_obj_scale[1])
                            particle_t = self.math.T(particle_loc[0], 0.0, particle_loc[1])

                            particle_transform = self.math.to_str(self.math.transform(particle_r,
                                                                                      particle_s, 
                                                                                      particle_t))

                            if not particle_obj_id in particle_transforms_dict:
                                particle_transforms_dict[particle_obj_id] = []
                                particle_transforms_dict[particle_obj_id] += particle_transform
                            else:
                                particle_transforms_dict[particle_obj_id] += particle_transform

                        k = 0
                        for key, val in particle_transforms_dict.items():
                            
                            sub_res_properties = {}
                            sub_res_properties["transform_format"] = 1
                            sub_res_properties["instance_count"] = int(len(val) / 12)
                            sub_res_properties["mesh"] = f"ExtResource( {particle_system_idx + k + 1} )"
                            sub_res_properties["transform_array"] = f"PoolVector3Array( {', '.join(val)} )"

                            self.tscn.add_sub_resource(res_type="MultiMesh", res_properties=sub_res_properties)

                            k += 1

                    break

        self.tscn.add_node(node_name=f"{os.path.splitext(self.blend_filename)[0]}", node_type="Spatial", node_parent=None, node_properties=None)

        current_obj = 1
        for key, val in self.blend_particle_dict["Emitter Objects"].items():
            ob_name = key
            ob_transform = val['Transform']
            ob_particle_objects = val["Particle Objects"]
            
            node_properties = {}
            node_properties["transform"] = f"Transform( {', '.join(ob_transform)} )"

            self.tscn.add_node(node_name=ob_name, node_type="Spatial", node_parent=".", node_properties=node_properties)

            #print(ob_particle_objects)

            i = 0
            for k, v in ob_particle_objects.items():

                part_node_properties = {}
                part_node_properties['multimesh'] = f"SubResource( {current_obj + i} )"

                part_ob_name = k
                
                self.tscn.add_node(node_name=part_ob_name, node_type="MultiMeshInstance", node_parent=ob_name, node_properties=part_node_properties)

                i += 1

        self.tscn.write(f"{project_dir}/test.tscn")