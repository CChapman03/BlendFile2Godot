import os
import sys
import bpy

sys.path.append(os.getcwd())

from convert_particles import Convert_Particles
from textures import Textures
from materials import Material

if __name__ == "__main__":
    
    project_dir = "../tests/test_project_dir"

    convert_p = Convert_Particles()
    convert_p.convert(project_dir)

    # material = Material()
    # material.get_all_objects_materials(project_dir)