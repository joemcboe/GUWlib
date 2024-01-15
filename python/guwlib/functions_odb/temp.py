from __future__ import print_function
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


def write_field_data_to_file(odb_path, output_file):
    # open the ODB file at the specified path
    my_print('Attempting to open {}.'.format(odb_path))
    odb = openOdb(path=odb_path)
    my_print('Odb file successfully opened.')

    # access step and assembly with index 0
    step = odb.steps.values()[0]
    instance_name = odb.rootAssembly.instances.keys()[0]
    instance = odb.rootAssembly.instances[instance_name]
    num_frames = len(step.frames)

    # read the position vector (in this particular case, it's positions in 0 direction because the line is horizontal)
    my_print('Reading in x, y values ...')
    frame = step.frames[0]
    displacement_values = frame.fieldOutputs['UT'].values
    node_x_values = [instance.getNodeFromLabel(v.nodeLabel).coordinates[0] for v in displacement_values]
    node_y_values = [instance.getNodeFromLabel(v.nodeLabel).coordinates[1] for v in displacement_values]
    my_print('Done! Starting to extract displacement data from {} frames ...'.format(num_frames))

    # read all displacements for all frames into a matrix, also save the points in time for each frame
    displacements_y = []
    displacements_x = []
    time_vector = []
    for kk, frame in enumerate(step.frames):
        if kk % 30 == 0:
            my_print('Extracting frame {} from {} ...'.format(kk, num_frames))
        try:
            # displacement_values = frame.fieldOutputs['UT'].values
            # displacements_y.append([v.data[1] for v in displacement_values])
            # displacements_x.append([v.data[0] for v in displacement_values])
            # time_vector.append(frame.frameValue)
            bulk_data = np.concatenate([np.copy(bulkDataBlock.data)
                                       for bulkDataBlock in frame.fieldOutputs['UT'].bulkDataBlocks], axis=0)
            displacements_x.append(bulk_data[:, 0])
            displacements_y.append(bulk_data[:, 1])
            time_vector.append(frame.frameValue)

        except:
            my_print("error for frame {}".format(kk))

    my_print('Starting to sort the data ...')
    # Convert to numpy arrays
    displacements_y_np = np.array(displacements_y)
    displacements_x_np = np.array(displacements_x)
    time_vector_np = np.array(time_vector)
    node_x_values_np = np.array(node_x_values)
    node_y_values_np = np.array(node_y_values)

    # Only for this special case (!) - separate top and bottom nodes
    y_values_unique = np.unique(node_y_values_np)
    y_values_unique = np.array([np.min(y_values_unique), np.max(y_values_unique)])
    labels = ['BOT', 'TOP']

    for kk, y_value in enumerate(y_values_unique):
        this_indexes = node_y_values_np == y_value
        this_node_x_values_np = node_x_values_np[this_indexes]
        this_displacements_y_np = displacements_y_np[:, this_indexes]
        this_displacements_x_np = displacements_x_np[:, this_indexes]

        # Get the indices that would sort the x vector
        sorted_indices = np.argsort(this_node_x_values_np)

        # Sort the x vector and the matrix columns using the sorted indices
        sorted_node_x_values_np = this_node_x_values_np[sorted_indices]
        sorted_displacements_y_np = this_displacements_y_np[:, sorted_indices]
        sorted_displacements_x_np = this_displacements_x_np[:, sorted_indices]

        # output_data = {'x_values': sorted_node_x_values_np,
        #                'y_values': node_y_values_np[this_indexes],
        #                't_values': time_vector_np,
        #                'displacements_y': sorted_displacements_y_np,
        #                'displacements_x': sorted_displacements_x_np}

        output_file_name = '{}_{}'.format(output_name, labels[kk])

        my_print('Starting to write compressed file {} ...'.format(output_file_name))
        # # Save the data to a binary file using pickle
        # output_file_name = output_file + '.pkl.gz'
        # with gzip.open(output_file_name, 'wb') as file:
        #     pickle.dump(output_data, file)
        np.savez_compressed(output_file_name,
                            x_values=sorted_node_x_values_np,
                            y_values=node_y_values_np[this_indexes],
                            t_values=time_vector_np,
                            displacements_y=sorted_displacements_y_np,
                            displacements_x=sorted_displacements_x_np)


def my_print(txt):
    print(txt, file=sys.__stdout__)


# main ----------------------------------------------------------------------------------------------------------------
arguments = sys.argv[1:]
path = arguments[-2]
output_name = arguments[-1]
my_print(path)
my_print(output_name)
write_field_data_to_file(odb_path=path, output_file=output_name)
