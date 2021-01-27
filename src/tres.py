import os

class TRES():

    def __init__(self):

        self.filename = ""
        
        self.type = "SpatialMaterial"
        self.format = 2
        self.load_steps = 3
        self.ext_resources = {}
        self.resources = {}

    def add_ext_resource(self, res_filename, res_type, res_dir="res://"):
        res_id = len(self.ext_resources.keys())
        
        self.ext_resources[res_id] = {"Filename" : res_filename, "Type" : res_type, "Path" : res_dir + res_filename}

    def add_resource(self, res_name, res_properties : dict):
        res_id = len(self.resources.keys())

        self.resources[res_id] = {"Name" : res_name, "Properties" : res_properties}

    def write(self, filename):

        with open(filename, 'w') as tres_file:

            tres_file.write(f"[gd_resource type=\"{self.type}\" load_steps={self.load_steps} format={self.format}]\n\n")
            
            for key, val in self.ext_resources.items():
                tres_file.write(f"[ext_resource path=\"{val['Path']}\" type=\"{val['Type']}\" id={key + 1}]\n")
            tres_file.write('\n')

            for key, val in self.resources.items():
                tres_file.write(f"[resource]\n")
                tres_file.write(f"resource_name = \"{val['Name']}\"\n")
                for p_key, p_val in val['Properties'].items():
                    tres_file.write(f"{p_key} = {p_val}\n")
                tres_file.write("\n")