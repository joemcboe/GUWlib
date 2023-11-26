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
    instance_nodes = instance.nodes

    # read the position vector (in this particular case, it's positions in 0 direction because the line is horizontal)
    frame = step.frames[0]
    values = frame.fieldOutputs['UT'].values
    node_x_values = [instance_nodes[v.nodeLabel-1].coordinates[0] for v in values]

    # read all displacements_z for all frames into a matrix, also save the points in time for each frame
    displacements_z = []
    displacements_x = []
    time_vector = []
    for frame in step.frames:
        time_vector.append(frame.frameValue)
        displacement_values = frame.fieldOutputs['UT'].values
        displacements_z.append([v.data[2] for v in displacement_values])
        displacements_x.append([v.data[0] for v in displacement_values])

    displacements_z_np = np.array(displacements_z)
    displacements_x_np = np.array(displacements_x)
    time_vector_np = np.array(time_vector)
    node_x_values_np = np.array(node_x_values)

    # Get the indices that would sort the x vector
    sorted_indices = np.argsort(node_x_values_np)
    my_print(node_x_values_np)
    my_print(sorted_indices)

    # Sort the x vector and the matrix columns using the sorted indices
    sorted_node_x_values_np = node_x_values_np[sorted_indices]
    sorted_displacements_z_np = displacements_z_np[:, sorted_indices]
    sorted_displacements_x_np = displacements_x_np[:, sorted_indices]

    output_data = {'x_values': sorted_node_x_values_np,
                   't_values': time_vector_np,
                   'displacements_z': sorted_displacements_z_np,
                   'displacements': sorted_displacements_z_np,
                   'displacements_x': sorted_displacements_x_np}

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
