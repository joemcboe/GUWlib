import odbAccess
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *

import numpy as np
import pickle
import gzip
import sys
import os

"""
This function helps to read in an ODB file written by Abaqus, check all available node sets for history output data
fields, collects the data along with the node set name, and writes it to a gzip compressed pkl file (binary). Use this
syntax:

abaqus cae noGUI=history_export_helper.py -- "path_to_output_folder "output_file_name"

where path_to_output_folder is the full path to a folder containing an *.ODB file, and "output_file_name" specifies
the name for the *.PKL.GZ-file written by this script. To read in the *.PKL.GZ-file, use

with gzip.open(output_file_name, 'rb') as file:
    loaded_data = pickle.load(file, encoding='latin1')
    
where output_file_name again specifies the name of the *.PKL.GZ file.
"""


def write_history_data_to_file(odb_path, output_file):
    # find the ODB file at the specified path
    odb_file = find_odb_file(odb_path)
    if odb_file is None:
        my_print("ODB file not found at given path.")
        raise ValueError('ODB file not found at given path.')
    else:
        my_print("ODB found at: {}".format(odb_file))

    # open the ODB file
    odb = openOdb(path=odb_file)

    # access step and assembly with index 0
    assembly = odb.rootAssembly
    step = odb.steps.values()[0]
    instance_name = odb.rootAssembly.instances.keys()[0]
    instance = odb.rootAssembly.instances[instance_name]

    # retrieve available node set names
    node_sets = odb.rootAssembly.instances[instance_name].nodeSets.keys()

    # create empty dictionary to store all data to be saved
    output_data = {}

    for node_set in node_sets:
        try:
            node = instance.nodeSets[node_set].nodes[0]
            point = odbAccess.HistoryPoint(node=node)
            region = step.getHistoryRegion(point=point)
            for output_var_name in ['U1', 'U2', 'U3']:
                data = np.array(region.historyOutputs[output_var_name].data)
                data_name = "{}_{}".format(node_set, output_var_name)
                output_data[data_name] = data

        except Exception as e:
            my_print("An exception occurred for nodeset {}: {}".format(node_set, e))

        #output_file_name = '{}\\{}.pkl.gz'.format(path, output_filename)
        output_file_name = '{}.pkl.gz'.format(path, output_file)

        # Save the data to a binary file using pickle
        with gzip.open(output_file_name, 'wb') as file:
            pickle.dump(output_data, file)


def find_odb_file(folder_path):
    # Check if the specified path exists
    if not os.path.exists(folder_path):
        return None

    # List all files in the specified folder
    files = os.listdir(folder_path)

    # Search for a file ending with '.odb'
    odb_file = next((file for file in files if file.lower().endswith('.odb')), None)

    if odb_file:
        return os.path.join(folder_path, odb_file)
    else:
        return None


def my_print(txt):
    print >> sys.__stdout__, txt


# main ----------------------------------------------------------------------------------------------------------------
arguments = sys.argv[1:]
path = arguments[-2]
output_name = arguments[-1]
my_print(path)
my_print(output_name)
write_history_data_to_file(odb_path=path, output_file=output_name)
