"""
This script recieves:
    - a list of directories
    - optional strings indicating whether to export history or field data
    - an int specifying how many parallel instances of ABAQUS/CAE should be started
    - an int specifying how many tasks should be spin up

This script will then scan these directories for any unprocessed .ODB files and then call the history / field export
helper functions on these files. A maximum of 10 jobs at the same time

This script can only run a UNIX environment with SLURM job manager installed.

"""
from slurm import generate_abaqus_job_script
import os
import sys
import ast
import subprocess


def find_directories(root_directory):
    odb_paths = []
    directory_paths = []

    for root, dirs, files in os.walk(root_directory):
        # Convert file names to lowercase for case-insensitive comparison
        lowercase_files = [file.lower() for file in files]

        if any(file.endswith(".odb") for file in lowercase_files) and not any(file.endswith(".npz") for file in lowercase_files):
            # If directory contains *.odb file but no *.pkl.gz file
            odb_file_path = [os.path.join(root, file) for file in files if file.lower().endswith(".odb")][0]
            odb_paths.append(odb_file_path)
            directory_paths.append(root)

    return odb_paths, directory_paths


if __name__ == "__main__":

    args = sys.argv[1:]

    # Extracting specific arguments based on their positions in the list
    model_file_paths_str = args[0]
    solver_n_nodes = int(args[1])
    solver_n_tasks_per_node = int(args[2])
    solver_partition = args[3]
    solver_max_time = args[4]

    # Parsing the string representation of a list into an actual list
    model_file_paths = ast.literal_eval(model_file_paths_str)

    odb_paths, directory_paths = find_directories('models')
    script_file = os.path.join('guwlibnano', 'guw_utility', 'odb_field_export.py')

    print(f"Found {len(odb_paths)} ODB files that have not been post processed ...")
