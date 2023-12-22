"""
This script automates uploading files to the cluster (Phoenix).
"""

from guwlib.functions_phoenix.ssh import *
from guwlib.functions_phoenix.slurm import *

# parameters set by the user -------------------------------------------------------------------------------------------

# specify the model files to upload to the cluster
model_files_local = [
    os.path.join('models', 'examples', 'example_01.py'),
    os.path.join('models', 'examples', 'crack_test.py')
]

# specify the directory on remote machine where GUWlib is located
remote_guwlib_path = '/work/y0106916/GUW_Simulation/GUW/python'

# resources to allocate for the ABAQUS/CAE execution (writing *.INP files)
# acceptable time formats include "minutes", "minutes:seconds", "hours:minutes:seconds", "days-hours",
# "days-hours:minutes" and "days-hours:minutes:seconds"

cae_n_nodes = 1
cae_n_tasks_per_node = 1
cae_partition = 'standard'
cae_max_time = "0:5:0"

# resources to allocate for each solver run (ABAQUS/Explicit, ABAQUS/Standard)
solver_n_nodes = 1
solver_n_tasks_per_node = 20
solver_partition = 'shortrun_small'
solver_max_time = "24:0:0"

# ----------------------------------------------------------------------------------------------------------------------
# copy the model files to the cluster
for model_file in model_files_local:
    file_name = os.path.basename(model_file)
    remote_path = f'{remote_guwlib_path}/models/{file_name}'
    copy_file_to_remote(model_file, remote_path, 'tubs_un', 'tubs_pw')
    print(f'Copied {file_name} to Phoenix.')

# generate a job file that calls phoenix_preprocesses_handler.py on the cluster ----------------------------------------
model_files_remote = ('"[' + ", ".join(["'models/{}'".format(os.path.basename(model_file))
                                        for model_file in model_files_local]) + ']"')
args = (f"{model_files_remote} {int(solver_n_nodes)} {int(solver_n_tasks_per_node)} "
        f"{solver_partition} {solver_max_time}")
job_file_name = 'run_preproc.job'
generate_python_job_script(output_file_path=job_file_name,
                           partition='standard',
                           n_nodes=cae_n_nodes,
                           n_tasks_per_node=cae_n_tasks_per_node,
                           max_time=cae_max_time,
                           slurm_job_name='PREPROC',
                           python_file='guwlib/functions_phoenix/phoenix_preprocess_submit_handler.py',
                           args=args,
                           working_dir=remote_guwlib_path)

# copy the master JOB file to the remote and submit it -----------------------------------------------------------------
copy_file_to_remote(job_file_name, f'{remote_guwlib_path}/{job_file_name}',
                    'tubs_un', 'tubs_pw')
run_commands_on_remote(command=f'cd {remote_guwlib_path} && sbatch {job_file_name}',
                       username_env_var='tubs_un',
                       password_env_var='tubs_pw')
