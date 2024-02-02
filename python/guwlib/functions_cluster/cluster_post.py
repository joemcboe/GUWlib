"""
This module handles automatic batch postprocessing of .ODB files, i.e. extraction of history or field output to
NumPy binary files (.NPZ).

The script is tailored as the server-side counterpart of ``guwlib.functions_batch.remote.extract_results()`` and is
intended to be run on a LINUX machine with SLURM workload manager. It scans the user-defined output directories for
unprocessed .ODB files. For each .ODB file found, a separate SLURM job is created and submitted to execute the
respective helper functions ``guwlib.functions_odb.field_export_helper`` or
``guwlib.functions_odb.history_export_helper`` on these files. The SLURM jobs are submitted in a sequential and / or
parallel manner.

Call this script with arguments specifying the directories to scan, the kind of output to process (history / field),
and parameters for the SLURM job. The required command line arguments of this script, in their order of appearance, are:

    - list[str]: directories that should be scanned (recursively) for results (.ODB files)
    - str: indicates whether to export history ("history") or field ("field") data
    - str: indicates which slurm partition to use (SLURM: --ntasks-per-node)
    - int: specifies how many parallel instances of ABAQUS/CAE should be started at most
    - int: specifies how many tasks (processes) should be used for each ABAQUS/CAE instance (SLURM: --ntasks-per-node)
    - str: specifies the maximum duration of the job (SLURM: --time)

Always make sure to run this script from the root directory of guwlib, otherwise the helper functions might not be
located correctly. A summary text file with the paths to all created .NPZ files is written to enable convenient batch
download of the processed files from the server to a client (``converted_odb_files.txt``).

Example usage:

    ``cluster_post.py "[results/dir1, results/dir2]" "history" "standard" "5" "10" "0:30:0"``

    Scans the directories ``results/dir1`` and ``results/dir2`` and their subdirectories for unprocessed .ODB files
    and executes the history export helper on all files found. Each extraction is submitted as a SLURM job on
    partition ``standard`` with 10 allocated processes, a maximum of 5 jobs will be submitted in parallel. Individual
    jobs will be cancelled due to time-out after 30 minutes.
"""
from slurm import generate_slurm_job
import os
import sys
import ast
import math
import subprocess
from datetime import datetime


def find_unprocessed_odb_files(root_directory):
    """
    Recursively scans the provided directory for folders that contain an .ODB file, but do not contain an .NPZ file.

    :param str root_directory: Path to the directory used as a root for the recursive scan.
    :return: Paths to the found unprocessed .ODB files.
    :rtype: list[str]
    """
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
    """
    Checks whether a file already exists and if it does, renames the existing file by appending "_archived_%d%m%y" to
    its file name.
    :param str file_path: Path to the file that is to be inspected.
    """
    if os.path.exists(file_path):
        current_date = datetime.now().strftime("%d%m%y")
        base_name, extension = os.path.splitext(file_path)
        new_file_name = f"{base_name}_archived_{current_date}{extension}"
        os.rename(file_path, new_file_name)


if __name__ == "__main__":

    # input argument parsing -------------------------------------------------------------------------------------------
    args = sys.argv[1:]
    dirs_to_scan = args[0]
    data_to_extract = args[1]
    partition = args[2]
    max_cae_instances = int(args[3])
    n_tasks = int(args[4])
    max_time = args[5]

    # evaluating the string representation of a list into a python list object
    dirs_to_scan = ast.literal_eval(dirs_to_scan)

    # scan the provided directories for unprocessed .ODB files ---------------------------------------------------------
    odb_paths = []
    for dir_to_scan in dirs_to_scan:
        odb_paths.extend(find_unprocessed_odb_files(dir_to_scan))
    print(f"Found {len(odb_paths)} ODB files that have not been post processed ...")

    job_file_paths = []
    npz_file_paths = []

    # for each unprocessed .ODB file, write a SLURM job file
    if data_to_extract == 'history':
        helper_script_file = os.path.join('guwlib', 'functions_odb', 'history_export_helper.py')
        for odb_path in odb_paths:
            job_file_name = os.path.join(os.path.dirname(odb_path), 'post.job')
            odb_file_name = os.path.basename(odb_path)
            generate_slurm_job(output_file_path=job_file_name,
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

    # submit the created SLURM jobs sequentially / parallel ------------------------------------------------------------
    n_chains = math.ceil(len(job_file_paths) / max_cae_instances)
    last_job_id = None

    for i, job_file in enumerate(job_file_paths):
        if i % n_chains == 0:
            command = f"sbatch {job_file}"
        else:
            command = f"sbatch --dependency=afterany:{last_job_id} {job_file}"
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        last_job_id = result.stdout.split()[-1].strip()

    # write out the file paths to the created .NPZ files to a text file ------------------------------------------------
    list_text_file = 'converted_odb_files.txt'
    archive_file(list_text_file)
    with open(list_text_file, 'w') as text_file:
        for path in npz_file_paths:
            text_file.write(path + '\n')
