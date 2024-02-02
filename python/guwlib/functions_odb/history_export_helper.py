"""
This script helps to export history output from an ABAQUS output database (.ODB) file to NumPy binary files (.NPZ).

The script opens the .ODB file using ABAQUS/CAE, checks all available node sets for history output data, and exports
the data. Data from each node set is stored in one individual NumPy array, which is structured like this:

    arr[0, :]       # time vector
    arr[1, :]       # U1 displacements
    arr[2, :]       # U2 displacements
    arr[3, :]       # U3 displacements

The .NPZ file is written to the same path as the ODB file. Call this script with one argument specifying
the path to the .ODB file to be processed:

    ``abaqus cae noGUI=history_export_helper.py -- "odb_path"``
"""

from __future__ import print_function

import odbAccess
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *

import numpy as np
import pickle
import sys
import os


def write_history_data_to_file(odb_path):
    """
    Opens the specified output database (.ODB) file in ABAQUS. Extracts the displacement history output (if
    available) for each node set of the first instance of the model. The TIME, U1, U2 and U3 vectors are
    concatenated in one NumPy matrix for each node set, and the matrices are then stored in an .NPZ file. If
    saving to .NPZ fails, pickle is used as a fallback (.PKL).

    :param str odb_path: Path to the .ODB file.
    """

    # open the ODB file at the specified path
    print('Attempting to open {}.'.format(odb_path), file=sys.__stdout__)
    odb = openOdb(path=odb_path)
    print('Odb file successfully opened.', file=sys.__stdout__)

    # access step and assembly with index 0
    assembly = odb.rootAssembly
    step = odb.steps.values()[0]
    instance_name = assembly.instances.keys()[0]
    instance = assembly.instances[instance_name]

    # retrieve available node set names
    node_sets = instance.nodeSets.keys()

    # create empty dictionary to store all data to be saved
    output_data = {}
    error_node_sets = []

    for node_set in node_sets:
        try:
            node = instance.nodeSets[node_set].nodes[0]
            point = odbAccess.HistoryPoint(node=node)
            region = step.getHistoryRegion(point=point)

            # np array is structured like this: [time, u1, u2, u3]
            t = np.array(region.historyOutputs['U1'].data)[:, 0]
            u1 = np.array(region.historyOutputs['U1'].data)[:, 1]
            u2 = np.array(region.historyOutputs['U2'].data)[:, 1]
            u3 = np.array(region.historyOutputs['U3'].data)[:, 1]
            data = np.vstack([t, u1, u2, u3])
            output_data[node_set] = data

        except Exception as e:
            error_node_sets.append(node_set)

    if error_node_sets:
        print('Skipped: ' + ', '.join(error_node_sets), file=sys.__stdout__)

    # set the output file name
    directory, full_filename = os.path.split(odb_path)
    filename, file_extension = os.path.splitext(full_filename)

    # save the data to a compressed NumPy .NPZ file
    print("Compressing and writing data ...", file=sys.__stdout__)
    try:
        output_file_name = '{}.npz'.format(os.path.join(directory, filename))
        np.savez_compressed(output_file_name, **output_data)
        print("Done! Data written to {}.".format(output_file_name), file=sys.__stdout__)
    except Exception as e:
        print("Error: {}\nTrying again with Pickle fallback ...".format(e), file=sys.__stdout__)

        # Save the dictionary using pickle
        output_file_name = '{}.pkl'.format(os.path.join(directory, filename))
        with open(output_file_name, 'wb') as f:
            pickle.dump(output_data, f)

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    arguments = sys.argv[1:]
    write_history_data_to_file(odb_path=arguments[-1])
