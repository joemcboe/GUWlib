"""
This script receives:
    - list of file paths to the model (.PY) files
    - slurm parameters for ABAQUS jobs

This script can only be run from the GUWlib working directory, otherwise it cannot correctly locate the results folder.
This script is intended to be run in a UNIX environment with SLURM installed.
"""
from slurm import generate_abaqus_job_script
import os
import sys
import ast
import subprocess


def find_inp_files_generate_job_script(directory_to_search, partition, n_nodes, n_tasks_per_node, max_time):
    # iterate through all *.INP-files in the simulation directory and generate *.JOB file
    job_file_paths = []
    for root, dirs, files in os.walk(directory_to_search):
        for file_name in files:
            if file_name.lower().endswith(".inp"):
                job_name = os.path.splitext(file_name)[0]
                job_file_path = os.path.join(root, job_name + '.job')

                print(f"{job_name} {job_file_path} {root}")

                generate_abaqus_job_script(output_file_path=job_file_path,
                                           partition=partition,
                                           n_nodes=n_nodes,
                                           n_tasks_per_node=n_tasks_per_node,
                                           max_time=max_time,
                                           slurm_job_name=job_name,
                                           working_dir=os.path.abspath(root),
                                           inp_file=file_name)
                job_file_paths.append(os.path.abspath(job_file_path))

    return job_file_paths


if __name__ == "__main__":

    args = sys.argv[1:]

    # extracting specific arguments based on their positions in the list
    model_file_paths_str = args[0]
    solver_n_nodes = int(args[1])
    solver_n_tasks_per_node = int(args[2])
    solver_partition = args[3]
    solver_max_time = args[4]

    # parsing the string representation of a list into an actual list
    model_file_paths = ast.literal_eval(model_file_paths_str)

    # iterate through model_file_paths, run CAE to create *.INP files and generate SLURM jobs for each of them ---------
    job_files = []
    for model_file_path in model_file_paths:
        # run ABAQUS/CAE on the model.py file to create *.INP files (one for each load case)
        model_file_name = os.path.splitext(os.path.basename(model_file_path))[0]
        print(f"Starting ABAQUS/CAE (*.INP file generation) on {model_file_name} ...")
        command = f"abaqus cae noGUI={model_file_path}"
        proc = subprocess.Popen(command, shell=True)
        proc.wait()

        # search for the *.INP files generated by ABAQUS/CAE and write a *.JOB file for each *.INP file
        # ABAQUS/CAE + GUWlib will write the *.INP files in the 'results' folder
        inp_file_dir = os.path.join('results', model_file_name)
        model_job_files = find_inp_files_generate_job_script(directory_to_search=inp_file_dir,
                                                             partition=solver_partition,
                                                             n_nodes=solver_n_nodes,
                                                             n_tasks_per_node=solver_n_tasks_per_node,
                                                             max_time=solver_max_time)
        job_files.extend(model_job_files)

    # build sequential submission chain --------------------------------------------------------------------------------
    last_job_id = None
    for i, job_file in enumerate(job_files):
        if i == 0:
            command = f"sbatch {job_file}"
        else:
            command = f"sbatch --dependency=afterany:{last_job_id} {job_file}"
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        last_job_id = result.stdout.split()[-1].strip()
