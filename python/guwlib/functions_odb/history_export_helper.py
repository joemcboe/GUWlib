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

abaqus cae noGUI=history_export_helper.py -- "odb_path" "output_file_name"

where path_to_output_folder is the full path to a folder containing an *.ODB file, and "output_file_name" specifies
the name for the *.PKL.GZ-file written by this script. To read in the *.PKL.GZ-file, use

with gzip.open(output_file_name, 'rb') as file:
    loaded_data = pickle.load(file, encoding='latin1')

where output_file_name again specifies the name of the *.PKL.GZ file.
"""


def write_history_data_to_file(odb_path, output_file):

    # open the ODB file
    odb = openOdb(path=odb_path)

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
            for output_var_name in ['U1', 'U2', 'U3']:
                data = np.array(region.historyOutputs[output_var_name].data)
                data_name = "{}_{}".format(node_set, output_var_name)
                output_data[data_name] = data
                my_print("Extracted {}".format(data_name))

        except Exception as e:
            error_node_sets.append(node_set)

    if error_node_sets:
        my_print('Skipped: '+', '.join(error_node_sets))

    output_file_name = '{}.pkl.gz'.format(output_file)

    # Save the data to a binary file using pickle
    my_print("Compressing data ...")
    with gzip.open(output_file_name, 'wb') as file:
        pickle.dump(output_data, file)
    my_print("Done! Data written to {}.".format(output_file_name))


def my_print(txt):
    print >> sys.__stdout__, txt


# main ----------------------------------------------------------------------------------------------------------------
arguments = sys.argv[1:]
path = arguments[-2]
output_name = arguments[-1]
write_history_data_to_file(odb_path=path, output_file=output_name)
