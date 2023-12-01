from guwlib.fe_model import FEModel
from guwlib.guw_objects.defect import *
from guwlib.guw_objects.loadcase import *
from guwlib.guw_objects.material import *
from guwlib.guw_objects.plate import *
from guwlib.guw_objects.signals import *
from guwlib.guw_objects.transducer import *


# import json
# import os
#
# file_dir = os.path.abspath(__file__)
# module_dir = os.path.dirname(file_dir)
# json_path = os.path.join(module_dir, 'data\\isotropic_materials.json')
#
# with open(json_path, 'r') as json_file:
#     MATERIAL_DATA = json.load(json_file)
#
# # Define constants for material names
# MATERIAL_NAMES = list(MATERIAL_DATA.keys())
# # You can also create individual constants for each material
# for material_name, material_properties in MATERIAL_DATA.items():
#     globals()[material_name] = material_name
