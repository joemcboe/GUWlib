import os

from guwlib.functions_cluster.slurm import *
from guwlib.functions_cluster.ssh import *


def build_and_solve(model_files_local, remote_guwlib_path, cae_slurm_settings, solver_slurm_settings,
                    hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """

    """
    # decompose dicts
    solver_n_nodes = solver_slurm_settings["n_nodes"]
    solver_n_tasks_per_node = solver_slurm_settings["n_tasks_per_node"]
    solver_max_time = solver_slurm_settings["max_time"]
    solver_partition = solver_slurm_settings["partition"]

    cae_n_nodes = cae_slurm_settings["n_nodes"]
    cae_n_tasks_per_node = cae_slurm_settings["n_tasks_per_node"]
    cae_max_time = cae_slurm_settings["max_time"]
    cae_partition = cae_slurm_settings["partition"]

    # retrieve the SSH username and password
    ssh_username, ssh_password = get_ssh_credentials(hostname)

    # copy the model files to the cluster
    for model_file in model_files_local:
        file_name = os.path.basename(model_file)
        remote_path = f'{remote_guwlib_path}/models/{file_name}'
        copy_file_to_remote(model_file, remote_path, ssh_username, ssh_password, hostname, port)
        print(f'Copied {file_name} to Phoenix.')

    # generate a job file that calls phoenix_preprocesses_handler.py on the cluster ------------------------------------
    model_files_remote = ('"[' + ", ".join(["'models/{}'".format(os.path.basename(model_file))
                                            for model_file in model_files_local]) + ']"')
    args = (f"{model_files_remote} {int(solver_n_nodes)} {int(solver_n_tasks_per_node)} "
            f"{solver_partition} {solver_max_time}")
    job_file_name = 'temp_preproc.job'

    generate_slurm_job(output_file_path=job_file_name,
                       partition=cae_partition,
                       n_nodes=cae_n_nodes,
                       n_tasks_per_node=cae_n_tasks_per_node,
                       max_time=cae_max_time,
                       slurm_job_name='PREPROC',
                       working_dir=remote_guwlib_path,
                       command=f"python3.9 guwlib/functions_cluster/cluster_pre.py {args}",
                       modules_to_load=("python/3.9.7", "software/abaqus/abaqus_2019"))

    # copy the master .JOB file to the remote and submit it ------------------------------------------------------------
    copy_file_to_remote(local_path=job_file_name, remote_path=f'{remote_guwlib_path}/{job_file_name}',
                        ssh_username=ssh_username, ssh_password=ssh_password, hostname=hostname, port=port)
    run_commands_on_remote(command=f'cd {remote_guwlib_path} && sbatch {job_file_name}',
                           ssh_username=ssh_username, ssh_password=ssh_password, hostname=hostname, port=port)
    os.remove(job_file_name)


def extract_results(directories_to_scan, data_to_extract, remote_guwlib_path, cae_slurm_settings,
                    max_parallel_cae_instances, hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """

    """
    # decompose dicts
    cae_n_tasks_per_node = cae_slurm_settings["n_tasks_per_node"]
    cae_max_time = cae_slurm_settings["max_time"]
    cae_partition = cae_slurm_settings["partition"]

    # retrieve the SSH username and password
    ssh_username, ssh_password = get_ssh_credentials(hostname)

    # arguments to pass to the cluster_post.py script
    directories_to_scan_str = ','.join(["'" + directory_to_scan + "'" for directory_to_scan in directories_to_scan])
    args = f'"[{directories_to_scan_str}]" "{data_to_extract}" "{cae_partition}" "{max_parallel_cae_instances}" ' \
           f'"{cae_n_tasks_per_node}" "{cae_max_time}"'
    working_dir = remote_guwlib_path

    # generate a job file
    job_file_name = 'temp_postproc.job'
    generate_slurm_job(output_file_path=job_file_name,
                       partition='standard',
                       n_nodes=1,
                       n_tasks_per_node=1,
                       max_time='0:5:0',
                       slurm_job_name='POSTPROC',
                       command=f"python3.9 guwlib/functions_cluster/cluster_post.py {args}",
                       modules_to_load=("python/3.9.7",),
                       working_dir=working_dir)

    # call the job file on the cluster
    copy_file_to_remote(local_path=job_file_name, remote_path=f'{remote_guwlib_path}/{job_file_name}',
                        ssh_username=ssh_username, ssh_password=ssh_password, hostname=hostname, port=port)
    run_commands_on_remote(command=f'cd {working_dir} && sbatch {job_file_name}',
                           ssh_username=ssh_username, ssh_password=ssh_password, hostname=hostname, port=port)
    os.remove(job_file_name)


def download_results(remote_guwlib_path, hostname, port):
    """

    """
    # retrieve the SSH username and password
    ssh_username, ssh_password = get_ssh_credentials(hostname)

    # download the converted_files.txt
    list_txt_file = 'converted_odb_files.txt'
    try:
        copy_file_from_remote(remote_path=f'{remote_guwlib_path}/{list_txt_file}',
                              local_path=f'{list_txt_file}',
                              ssh_username=ssh_username, ssh_password=ssh_password,
                              hostname=hostname, port=port)

    except FileNotFoundError:
        print(f"File {remote_guwlib_path}/{list_txt_file} is not available on the remote machine. Make"
              f"sure that you specified the correct working_dir and that you have already extracted"
              f"results to .NPZ files. This script is for downloading only.")

    # for each line in the converted_files.txt, extract the remote paths and add them to a list
    file_paths = []
    with open(list_txt_file, 'r') as file:
        for line in file:
            file_paths.append(line.strip())

    # for each file in the list, download the file from the file path from src to dst
    for file_path in file_paths:
        # when copying the remote files to the local machine, flatten the directory out by one layer
        file_name = os.path.basename(file_path)
        parent_directory = os.path.dirname(os.path.dirname(file_path))
        local_path = os.path.join(parent_directory, file_name)
        copy_file_from_remote(remote_path=f'{remote_guwlib_path}/{file_path}',
                              local_path=local_path,
                              ssh_username=ssh_username, ssh_password=ssh_password,
                              hostname=hostname, port=port)
        print(f"Copied {file_name} to {parent_directory}/.")
