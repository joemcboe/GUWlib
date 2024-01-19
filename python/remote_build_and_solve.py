"""
This script automates uploading files to the cluster (Phoenix). This script will trigger the cluster_pre.py script.

"""

from guwlib.functions_cluster.ssh import *
from guwlib.functions_cluster.slurm import *

# parameters set by the user -------------------------------------------------------------------------------------------

# specify the model files to upload to the cluster
model_files_local = [
    # stack 1 - started 24th december
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_top.py'),
    # os.path.join('models', 'alu3a', 'alu3a_pristine_top.py'),

    # stack 2 - started 27th december
    # os.path.join('models', 'alu3a', 'alu3a_pristine_bot.py'),
    # os.path.join('models', 'alu3a', 'alu3a_pristine_symm.py'),
    # os.path.join('models', 'alu3a', 'alu3a_pristine_asymm.py'),
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_bot.py'),
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_symm.py'),
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_asymm.py'),

    # stack 3 - started 1st january
    # os.path.join('models', 'alu3a', 'alu3a_central_hole15_top.py'),
    # os.path.join('models', 'alu3a', 'alu3a_farfield_hole10_top.py'),
    # os.path.join('models', 'alu3a', 'alu3a_central_2_hole10_top.py'),
    # os.path.join('models', 'alu3a', 'alu3a_crack_45_central_top.py'),

    os.path.join('models', 'testing', 'pristine_far_piezos.py'),
]

# specify the directory on remote machine where GUWlib is located
remote_guwlib_path = '/beegfs/work/y0106916/GUW2024/'

# resources to allocate for the ABAQUS/CAE execution (writing *.INP files)
#   cae_max_time is the total time for to process all model files
#   acceptable time formats include "minutes", "minutes:seconds", "hours:minutes:seconds", "days-hours",
#   "days-hours:minutes" and "days-hours:minutes:seconds" (SLURM syntax)

cae_n_nodes = 1
cae_n_tasks_per_node = 20           # 20
cae_partition = 'fat'          # 'standard'
cae_max_time = "3:0:0"            # '3-0:0:0'

# resources to allocate for each individual solver run (ABAQUS/Explicit, ABAQUS/Standard)
solver_n_nodes = 1
solver_n_tasks_per_node = 20          # 20
solver_partition = 'fat'
solver_max_time = "1-0:0:0"         # '1-0:0:0'

# ---------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                                                                                                                      #
#                                     !DO NOT CHANGE THE FOLLOWING SECTIONS!                                           #
#                                                                                                                      #
#                                                                                                                      #
# ---------------------------------------------------------------------------------------------------------------------#
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
                           partition=cae_partition,
                           n_nodes=cae_n_nodes,
                           n_tasks_per_node=cae_n_tasks_per_node,
                           max_time=cae_max_time,
                           slurm_job_name='PREPROC',
                           python_file='guwlib/functions_cluster/cluster_pre.py',
                           args=args,
                           working_dir=remote_guwlib_path)

# copy the master JOB file to the remote and submit it -----------------------------------------------------------------
copy_file_to_remote(job_file_name, f'{remote_guwlib_path}/{job_file_name}',
                    'tubs_un', 'tubs_pw')
run_commands_on_remote(command=f'cd {remote_guwlib_path} && sbatch {job_file_name}',
                       username_env_var='tubs_un',
                       password_env_var='tubs_pw')
