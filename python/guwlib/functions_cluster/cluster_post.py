"""
This script recieves:
    - a list of directories that should be scanned (recursively) for results (ODB files)
    - string indicating whether to export history or field data
    - an int specifying how many parallel instances of ABAQUS/CAE should be started at most
    - an int specifying how many tasks should be used for each ABAQUS/CAE instance (RAM)

This script will then scan these directories for any unprocessed .ODB files and then call the history / field export
helper functions on these files.

This script can only run a UNIX environment with SLURM job manager installed. !Run this script from the GUWlib root
directory!

Example:
    cluster_post.py "[models/dir1, models/dir2]" "history" "5" "1"


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

    # extracting specific arguments based on their positions in the list
    dirs_to_scan = args[0]
    data_to_extract = args[1]
    max_cae_instances = int(args[2])
    n_slurm_tasks = int(args[3])

    # parsing the string representation of a list into an actual list
    dirs_to_scan = ast.literal_eval(dirs_to_scan)

    # ------------------------------------------------------------------------------------------------------------------
    script_file_history_export = os.path.join('guwlib', 'functions_odb', 'history_export_helper.py')
    script_file_field_export = os.path.join('guwlib', 'functions_odb', 'field_export_helper.py')

    for dir_to_scan in dirs_to_scan:
        odb_paths, directory_paths = find_directories('models')
        print(f"Found {len(odb_paths)} ODB files that have not been post processed ...")

    # for each odb_path in odb_paths, create and run a SLURM job

