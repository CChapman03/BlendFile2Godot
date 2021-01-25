import os

class TSCN():

    def __init__(self):

        self.filename = ""
        
        self.format = 2
        self.load_steps = 4
        self.ext_resources = {}
        self.sub_resources = {}
        self.nodes = {}

    def add_ext_resource(self, res_filename, res_type, res_dir="res://"):
        res_id = len(self.ext_resources.keys())
        
        self.ext_resources[res_id] = {"Filename" : res_filename, "Type" : res_type, "Path" : res_dir + res_filename}

    def add_sub_resource(self, res_type, res_properties : dict):
        res_id = len(self.sub_resources.keys())

        self.sub_resources[res_id] = {"Type" : res_type, "Properties" : res_properties}

    def add_node(self, node_name, node_type, node_parent, node_properties : dict):
        self.nodes[len(self.nodes.keys())] = {"Name" : node_name, "Type" : node_type, "Parent" : node_parent, "Properties" : node_properties}

    def write(self, filename):

        with open(filename, 'w') as tscn_file:

            tscn_file.write(f"[gd_scene load_steps={self.load_steps} format={self.format}]\n\n")
            
            for key, val in self.ext_resources.items():
                tscn_file.write(f"[ext_resource path=\"{val['Path']}\" type=\"{val['Type']}\" id={key}]\n")

            for key, val in self.sub_resources.items():
                tscn_file.write(f"[sub_resource type=\"{val['Type']}\" id={key}]\n")
                for p_key, p_val in val['Properties'].items():
                    tscn_file.write(f"{p_key} = {p_val}\n")
                tscn_file.write("\n")
            
            for key, val in self.nodes.items():
                tscn_file.write(f"[node name=\"{val['Name']}\" type=\"{val['Type']}\"")
                if val['Parent'] != None:
                    tscn_file.write(f"parent=\"{val['Parent']}\"]\n")
                else:
                    tscn_file.write(f"]\n")
                
                if val['Properties'] != None:
                    for p_key, p_val in val['Properties'].items():
                        tscn_file.write(f"{p_key} = {p_val}\n")
                    tscn_file.write("\n")
