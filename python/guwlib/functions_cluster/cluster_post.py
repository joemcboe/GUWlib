"""
This script receives:
    - a list of directories that should be scanned (recursively) for results (ODB files)
    - string indicating whether to export history or field data
    - a string indicating which slurm partition to use
    - an int specifying how many parallel instances of ABAQUS/CAE should be started at most
    - an int specifying how many tasks should be used for each ABAQUS/CAE instance (RAM)
    a string specifying how long one extraction should take at most

This script will then scan these directories for any unprocessed .ODB files and then call the history / field export
helper functions on these files.

This script can only run a UNIX environment with SLURM job manager installed. !Run this script from the GUWlib root
directory!

Example:
    cluster_post.py "[models/dir1, models/dir2]" "history" "standard" "5" "1" "0:30:0"


"""
from slurm import generate_command_job_script
import os
import sys
import ast
import math
import subprocess
from datetime import datetime


def find_odb_files(root_directory):
    file_paths = []

    print(f"Searching {root_directory} ...")

    for root, dirs, files in os.walk(root_directory):
        # convert file names to lowercase for case-insensitive comparison
        lowercase_files = [file.lower() for file in files]

        # if directory contains *.ODB file but no *.NPZ file
        if (any(file.endswith(".odb") for file in lowercase_files) and
                not any(file.endswith(".npz") for file in lowercase_files)):
            odb_file_path = [os.path.join(root, file) for file in files if file.lower().endswith(".odb")]
            file_paths.extend(odb_file_path)

    return file_paths


def archive_file(file_path):
    if os.path.exists(file_path):
        current_date = datetime.now().strftime("%d%m%y")
        base_name, extension = os.path.splitext(file_path)
        new_file_name = f"{base_name}_archived_{current_date}{extension}"
        os.rename(file_path, new_file_name)


if __name__ == "__main__":

    args = sys.argv[1:]

    # extracting specific arguments based on their positions in the list
    dirs_to_scan = args[0]
    data_to_extract = args[1]
    partition = args[2]
    max_cae_instances = int(args[3])
    n_tasks = int(args[4])
    max_time = args[5]

    # parsing the string representation of a list into an actual list
    dirs_to_scan = ast.literal_eval(dirs_to_scan)

    # ------------------------------------------------------------------------------------------------------------------
    odb_paths = []
    for dir_to_scan in dirs_to_scan:
        odb_paths.extend(find_odb_files(dir_to_scan))
    print(f"Found {len(odb_paths)} ODB files that have not been post processed ...")

    job_file_paths = []
    npz_file_paths = []

    if data_to_extract == 'history':
        helper_script_file = os.path.join('guwlib', 'functions_odb', 'history_export_helper.py')
        for odb_path in odb_paths:
            job_file_name = os.path.join(os.path.dirname(odb_path), 'post.job')
            odb_file_name = os.path.basename(odb_path)
            generate_command_job_script(output_file_path=job_file_name,
                                        partition=partition,
                                        n_nodes=1,
                                        n_tasks_per_node=n_tasks,
                                        max_time=max_time,
                                        slurm_job_name=odb_file_name,
                                        working_dir=os.getcwd(),
                                        command=f"abaqus cae noGUI={helper_script_file} -- {odb_path}")
            job_file_paths.append(os.path.abspath(job_file_name))

            npz_file_name = os.path.join(os.path.dirname(odb_path), os.path.splitext(odb_file_name)[0] + '.npz')
            npz_file_paths.append(npz_file_name)

    if data_to_extract == 'field':
        helper_script_file = os.path.join('guwlib', 'functions_odb', 'field_export_helper.py')
        raise NotImplementedError('Field export helper function not yet implemented.')

    # build sequential submission chain --------------------------------------------------------------------------------
    n_chains = math.ceil(len(job_file_paths) / max_cae_instances)
    last_job_id = None

    for i, job_file in enumerate(job_file_paths):
        if i % n_chains == 0:
            command = f"sbatch {job_file}"
        else:
            command = f"sbatch --dependency=afterany:{last_job_id} {job_file}"
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        last_job_id = result.stdout.split()[-1].strip()

    # write out the npz file paths as a text file ----------------------------------------------------------------------
    list_text_file = 'converted_odb_files.txt'
    archive_file(list_text_file)
    with open(list_text_file, 'w') as text_file:
        for path in npz_file_paths:
            text_file.write(path + '\n')
