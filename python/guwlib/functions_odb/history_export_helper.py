"""
This script helps to read in and export an ABAQUS .ODB file. It checks all available node sets for history output data
fields, collects the displacement data along with the node set name, and writes it to a .NPZ (compressed NumPy) file.
To call this script, use this syntax:

.. code-block::
    abaqus cae noGUI=history_export_helper.py -- "odb_path"

where ``path_to_output_folder`` is the full path to the *.ODB file. The .NPZ file is written to the same path as the
ODB file. Access the content of the written files like this:

.. code-block::
    data = numpy.load(my_file)
    for key in data.keys():
        print(key)
    data.close()

Each array stored in the NPZ file is structured like this:

.. code-block::
    arr = data[key]
    arr[0, :]       # time vector
    arr[1, :]       # U1 displacements
    arr[2, :]       # U2 displacements
    arr[3, :]       # U3 displacements
"""

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


def write_history_data_to_file(odb_path):
    """
    Opens the specified output database (.ODB) file in ABAQUS. It extracts the displacement history output (if
    available) for all node sets in the first instance of the model. The time, U1, U2 and U3 vectors are concatenated
    in one NumPy matrix for each node set, and the matrices are then stored in a .NPZ file.

    :param str odb_path: Path to the .ODB file.
    """

    # open the ODB file at the specified path
    my_print('Attempting to open {}.'.format(odb_path))
    odb = openOdb(path=odb_path)
    my_print('Odb file successfully opened.')

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

            # np array is structured like this: [time; u1; u2; u3]
            t = np.array(region.historyOutputs['U1'].data)[:, 0]
            u1 = np.array(region.historyOutputs['U1'].data)[:, 1]
            u2 = np.array(region.historyOutputs['U2'].data)[:, 1]
            u3 = np.array(region.historyOutputs['U3'].data)[:, 1]
            data = np.vstack([t, u1, u2, u3])

            output_data[node_set] = data
            my_print("Extracted {}".format(data_name))

        except Exception as e:
            error_node_sets.append(node_set)

    if error_node_sets:
        my_print('Skipped: ' + ', '.join(error_node_sets))

    # Set the output file name
    directory, full_filename = os.path.split(odb_path)
    filename, file_extension = os.path.splitext(full_filename)
    output_file_name = '{}.npz'.format(os.path.join(directory, filename))

    # Save the data to a binary file using pickle
    my_print("Compressing and writing data ...")
    np.savez_compressed(output_file_name,
                        **output_data)
    my_print("Done! Data written to {}.".format(output_file_name))


def my_print(txt):
    print(txt, file=sys.__stdout__)


# main -----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    arguments = sys.argv[1:]
    write_history_data_to_file(odb_path=arguments[-1])
