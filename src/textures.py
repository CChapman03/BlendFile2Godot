import bpy
import random
import mathutils
import sys
import shutil

import os

sys.path.append(os.getcwd())

class Textures():

    def __init__(self):

        self.textures = []

    def get_textures(self, project_dir):
        
        for img in bpy.data.images:
            filename = img.filepath_raw.replace("../", "").replace("//", "/")
            
            if filename != "":
                print(f"{project_dir}/{os.path.basename(filename)}")

                self.textures += [f"{os.path.basename(filename)}"]

                shutil.copyfile(filename, f"{project_dir}/{os.path.basename(filename)}")