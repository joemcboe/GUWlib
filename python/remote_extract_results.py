from guwlib.functions_cluster.ssh import *
from guwlib.functions_cluster.slurm import *
import re
import ast

"""
This script automates the extraction of ABAQUS results (.ODB files) from a remote UNIX system with SLURM installed. 
This script runs on a local computer. It connects to the remote machine via SSH and it starts the cluster_post.py
script there as a SLURM job.
  
"""

# parameters set by the user -------------------------------------------------------------------------------------------
directories_to_scan = [
    # 'results/alu3a_central_2_hole10_top/'
    # 'results/alu3a_pristine_top/',
    # 'results/alu3a_pristine_bot/',
    # 'results/alu3a_pristine_symm/',
    #
    # 'results/alu3a_central_hole10_top/',
    # 'results/alu3a_central_hole10_bot/',
    # 'results/alu3a_central_hole10_symm/',
    #
    # 'results/alu3a_central_hole15_top/',
    # 'results/alu3a_farfield_hole10_top/',
    # 'results/alu3a_crack_45_central_top/',

    # 'results/pristine_far_piezos/'
    'results/alu3a_pristine_asymm/',

]

remote_guwlib_path = '/beegfs/work/y0106916/GUW_Simulation/GUW/python/'  # forward slash at the end!
output_type = 'history'
partition = 'standard'
max_cae_instances = 10
n_tasks = 10
max_time = "0:15:0"

# ---------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                                                                                                                      #
#                                     !DO NOT CHANGE THE FOLLOWING SECTIONS!                                           #
#                                                                                                                      #
#                                                                                                                      #
# ---------------------------------------------------------------------------------------------------------------------#

# arguments to pass to the cluster_post.py script
directories_to_scan_str = ','.join(["'" + directory_to_scan + "'" for directory_to_scan in directories_to_scan])
args = f'"[{directories_to_scan_str}]" "{output_type}" "{partition}" "{max_cae_instances}" "{n_tasks}" "{max_time}"'
working_dir = remote_guwlib_path

# generate a job file
job_file_name = 'run_postproc.job'
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
copy_file_to_remote(job_file_name, f'{working_dir}/{job_file_name}',
                    'tubs_un', 'tubs_pw')
cmd = f'cd {working_dir} && sbatch {job_file_name}'
run_commands_on_remote(command=cmd,
                       username_env_var='tubs_un',
                       password_env_var='tubs_pw')
