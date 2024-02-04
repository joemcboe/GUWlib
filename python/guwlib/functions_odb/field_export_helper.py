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


def write_field_data_to_file(odb_path):
    """
    Opens the specified output database (.ODB) file in ABAQUS. Extracts the displacement field output (if
    available) and saves it to an .NPZ file. If saving to .NPZ fails, pickle is used as a fallback (.PKL format).

    Node connectivity data is not exported, which is why it is not usually possible to create surface plots from
    the exported data (like in ABAQUS/Viewer).

    :param str odb_path: Path to the .ODB file.
    """
    # open the ODB file at the specified path
    my_print('Attempting to open {}.'.format(odb_path))
    odb = openOdb(path=odb_path)
    my_print('Odb file successfully opened.')

    # access step and assembly with index 0
    step = odb.steps.values()[0]
    instance_name = odb.rootAssembly.instances.keys()[0]
    instance = odb.rootAssembly.instances[instance_name]
    num_frames = len(step.frames)

    # read the x, y, z positions of the nodes
    my_print('Reading in x, y, z node positions ...')
    frame = step.frames[0]
    displacement_values = frame.fieldOutputs['UT'].values
    node_x_values = [instance.getNodeFromLabel(v.nodeLabel).coordinates[0] for v in displacement_values]
    node_y_values = [instance.getNodeFromLabel(v.nodeLabel).coordinates[1] for v in displacement_values]
    node_z_values = [instance.getNodeFromLabel(v.nodeLabel).coordinates[2] for v in displacement_values]
    my_print('Starting to extract displacement data from {} frames ...'.format(num_frames))

    # read all displacements for all frames into a matrix, also save the points in time for each frame
    displacements_y = []
    displacements_x = []
    displacements_z = []
    time_vector = []
    for kk, frame in enumerate(step.frames):
        if kk % 30 == 0:
            my_print('Extracting frame {} from {} ...'.format(kk, num_frames))
        try:
            bulk_data = np.concatenate([np.copy(bulkDataBlock.data)
                                        for bulkDataBlock in frame.fieldOutputs['UT'].bulkDataBlocks], axis=0)
            displacements_x.append(bulk_data[:, 0])
            displacements_y.append(bulk_data[:, 1])
            displacements_z.append(bulk_data[:, 2])
            time_vector.append(frame.frameValue)

        except Exception as e:
            my_print("Error {} for frame {}.".format(e, kk))

    # Convert to numpy arrays
    displacements_y_np = np.array(displacements_y)
    displacements_x_np = np.array(displacements_x)
    displacements_z_np = np.array(displacements_z)

    time_vector_np = np.array(time_vector)
    node_x_values_np = np.array(node_x_values)
    node_y_values_np = np.array(node_y_values)
    node_z_values_np = np.array(node_z_values)

    output_data = {"x_values": node_x_values_np,
                   "y_values": node_y_values_np,
                   "z_values": node_z_values_np,
                   "t_values": time_vector_np,
                   "displacements_y": displacements_y_np,
                   "displacements_x": displacements_x_np,
                   "displacements_z": displacements_z_np}

    # set the output file name
    directory, full_filename = os.path.split(odb_path)
    filename, file_extension = os.path.splitext(full_filename)

    # save the data to a compressed NumPy .NPZ file
    my_print("Compressing and writing data ...")
    try:
        output_file_name = '{}_field.npz'.format(os.path.join(directory, filename))
        np.savez_compressed(output_file_name, **output_data)
        print("Done! Data written to {}.".format(output_file_name), file=sys.__stdout__)
    except Exception as e:
        print("Error: {}\nTrying again with Pickle fallback ...".format(e), file=sys.__stdout__)

        # Save the dictionary using pickle
        output_file_name = '{}.pkl'.format(os.path.join(directory, filename))
        with open(output_file_name, 'wb') as f:
            pickle.dump(output_data, f)


def my_print(txt):
    print(txt, file=sys.__stdout__)


# main ----------------------------------------------------------------------------------------------------------------
arguments = sys.argv[1:]
path = arguments[-1]
write_field_data_to_file(odb_path=path)
