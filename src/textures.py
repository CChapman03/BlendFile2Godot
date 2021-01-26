import bpy
import random
import mathutils
import sys
import shutil

import os

sys.path.append(os.getcwd())

class Textures():

    def __init__(self):

        pass

    def copy_textures(self, project_dir):
        
        for img in bpy.data.images:
            print(img.filepath_raw)

            shutil.copyfile(os.path.abspath(img.filepath), f"{project_dir}/{os.path.basename(img.filepath)}")