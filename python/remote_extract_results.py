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
    'results/small_b'
]

remote_guwlib_path = '/work/y0106916/GUW_Testing/python'
output_type = 'history'
partition = 'standard'
max_cae_instances = 5
n_tasks = 1
max_time = "0:5:0"

# ---------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                                                                                                                      #
#                                     !DO NOT CHANGE THE FOLLOWING SECTIONS!                                           #
#                                                                                                                      #
#                                                                                                                      #
# ---------------------------------------------------------------------------------------------------------------------#

# arguments to pass to the cluster_post.py script
directories_to_scan_str = ','.join(["'"+directory_to_scan+"'" for directory_to_scan in directories_to_scan])
args = f'"[{directories_to_scan_str}]" "{output_type}" "{partition}" "{max_cae_instances}" "{n_tasks}" "{max_time}"'
working_dir = remote_guwlib_path

# generate a job file
job_file_name = 'temp.job'
generate_python_job_script(output_file_path=job_file_name,
                           partition='standard',
                           n_nodes=1,
                           n_tasks_per_node=1,
                           max_time='0:5:0',
                           slurm_job_name='POSTPROC',
                           python_file='guwlib/functions_cluster/cluster_post.py',
                           args=args,
                           working_dir=working_dir)

# call the job file on the cluster
copy_file_to_remote(job_file_name, f'{working_dir}/{job_file_name}',
                    'tubs_un', 'tubs_pw')
cmd = f'cd {working_dir} && sbatch {job_file_name}'
run_commands_on_remote(command=cmd,
                       username_env_var='tubs_un',
                       password_env_var='tubs_pw')
