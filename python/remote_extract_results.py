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
# specify the model files to upload to the cluster
model_files_local = [
    os.path.join('models/convergence_test', 'convergence_pristine_20_x_10.py')
]

working_dir = '/work/y0106916/'


# ----------------------------------------------------------------------------------------------------------------------
# compile a list of result folders from the script names
result_directories = [f"'results/{os.path.splitext(os.path.basename(model_file_path))[0]}'"
                      for model_file_path in model_files_local]
args = '"[' + ', '.join(result_directories) + ']"'

# generate a job file
job_file_name = 'temp.job'
generate_python_job_script(output_file_path=job_file_name,
                           partition='standard',
                           n_nodes=1,
                           n_tasks_per_node=1,
                           max_time_in_h=2,
                           slurm_job_name='collect',
                           python_file='guwlib/trash/phoenix_post_process.py',
                           args=args,
                           working_dir=working_dir)

# call the job file on the cluster
copy_file_to_remote(job_file_name, f'{working_dir}/{job_file_name}',
                    'tubs_username', 'tubs_password')
cmd = f'cd {working_dir} && sbatch {job_file_name}'
console_output = run_commands_on_remote(command=cmd, username_env_var='tubs_username', password_env_var='tubs_password')


