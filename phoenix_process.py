"""
Phoenix Process Script

This script is designed to be executed on the Phoenix cluster, facilitating the creation and submission
of ABAQUS simulations. It automates the process of converting GUWLIB model files (.py) into input files
(.INP) using ABAQUS/CAE, generating corresponding SLURM job scripts (.JOB), and submitting them for parallel
execution. The SLURM job scripts (.JOB) include commands to run the ABAQUS solver on the created .INP files.

Note: The script assumes a configured SLURM environment with ABAQUS and PYTHON installed for proper execution.

Usage:
    python phoenix_process.py "<model_file_paths>" [n_nodes] [n_tasks_per_node] [partition] [max_time]

Arguments:
    - model_file_paths (str): A string representation of a Python list containing paths to GUWLIB model
      files (.py). Enclose the list in quotes, e.g., "['models/model_file_1.py', 'models/model_file_2.py']".
    - n_nodes (int): Number of compute nodes to request for each job (default: 1).
    - n_tasks_per_node (int): Number of tasks (CPUs) to allocate per node (default: 1).
    - partition (str): Name of the SLURM partition to allocate resources from (default: 'standard').
    - max_time (int): Maximum time in hours for each job to run (default: 12).

Example:
    python phoenix_process.py "['models/my_model.py', 'models/another_model.py']" 2 10 "shortrun_small" 24
"""

import os
import sys
import subprocess
import ast
from guwlib.functions_phoenix.slurm import generate_abaqus_job_script


def submit_model_files(model_file_paths, n_nodes, n_tasks_per_node, partition, max_time):
    """
    Submits ABAQUS simulations for a set of GUW model files (*.py) using SLURM job scripts. This function
    is intended to be run on an environment with SLURM, ABAQUS and PYTHON installed (e.g. Phoenix Cluster).

    :param List[str] model_file_paths: paths to GUWLIB model files (.py).
    :param int n_nodes: number of compute nodes to request for each job.
    :param int n_tasks_per_node: number of tasks (CPUs) to allocate per node.
    :param str partition: name of the SLURM partition to allocate resources from.
    :param int max_time: maximum time in hours for each job to run.

    :return: None

    The function takes a list of ABAQUS model files, runs ABAQUS/CAE to generate corresponding *.INP files,
    creates SLURM job scripts for each generated *.INP file, and submits the jobs to the specified SLURM
    partition. Each job is identified by a unique SLURM job name based on its position in the input list.

    Example:
    submit_model_files(
        model_file_paths=['model1.py', 'model2.py'],
        n_nodes=4,
        n_tasks_per_node=8,
        partition='shortrun_small',
        max_time=24
    )
    """

    for k, model_file_path in enumerate(model_file_paths):

        # run ABAQUS/CAE on the model.py file to create *.INP file
        model_file_name, _ = os.path.splitext(os.path.basename(model_file_path))
        command = f"abaqus cae noGUI={model_file_path}"
        proc = subprocess.Popen(command, shell=True)
        proc.wait()

        # iterate through all *.INP-files in the simulation directory and generate *.JOB file
        i = 0
        for root, dirs, files in os.walk(os.path.join('results', model_file_name)):
            for file_name in files:
                if file_name.endswith(".inp"):
                    i = i + 1
                    file_name = os.path.splitext(file_name)[0]
                    job_file_path = os.path.join(root, file_name)

                    # generate a SLURM job file
                    generate_abaqus_job_script(output_file_path=job_file_path + '.job',
                                               partition=partition,
                                               n_nodes=n_nodes,
                                               n_tasks_per_node=n_tasks_per_node,
                                               max_time_in_h=max_time,
                                               slurm_job_name=f'{k}_{i}',
                                               inp_file=file_name + '.inp',
                                               working_dir=root)

                    # submit the job
                    command = f"cd {root} && sbatch {file_name}.job"

                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = proc.communicate()

                    if proc.returncode == 0:
                        # Job submission successful, extract the job ID from the output
                        job_id = out.decode().strip().split()[-1]
                        print(f"Submitted. JOB_ID={job_id}")

                    else:
                        print(f"Job submission failed. Error: {err.decode()}")


if __name__ == "__main__":
    # Parsing command-line arguments
    script_name = sys.argv[0]
    arguments = sys.argv[1:]

    # Extracting specific arguments based on their positions in the list
    model_file_paths_str = arguments[0] if arguments else "[]"
    n_nodes = int(arguments[1]) if len(arguments) > 1 else 1
    n_tasks_per_node = int(arguments[2]) if len(arguments) > 2 else 1
    partition = arguments[3] if len(arguments) > 3 else 'standard'
    max_time = int(arguments[4]) if len(arguments) > 4 else 12

    # Parsing the string representation of a list into an actual list
    model_file_paths = ast.literal_eval(model_file_paths_str)

    if model_file_paths is not None:
        submit_model_files(model_file_paths=model_file_paths, n_nodes=n_nodes, n_tasks_per_node=n_tasks_per_node,
                           partition=partition, max_time=max_time)
