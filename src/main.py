import os
import sys
import bpy

sys.path.append(os.getcwd())

from convert_particles import Convert_Particles
from textures import Textures

if __name__ == "__main__":
    
    project_dir = "../tests/test_project_dir"

    convert_p = Convert_Particles()
    convert_p.convert(project_dir)

    textures = Textures()
    textures.copy_textures(project_dir)