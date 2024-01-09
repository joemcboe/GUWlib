"""
This script automates uploading files to the cluster (Phoenix).
"""

from guwlib.functions_phoenix.ssh import *
from guwlib.functions_phoenix.slurm import *

# parameters set by the user -------------------------------------------------------------------------------------------

# specify the model files to upload to the cluster
model_files_local = [
    # stack 1 - started 24th december
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_top.py'),
    # os.path.join('models', 'alu3a', 'alu3a_pristine_top.py'),

    # stack 2 - started 27th decmeber
    # os.path.join('models', 'alu3a', 'alu3a_pristine_bot.py'),
    # os.path.join('models', 'alu3a', 'alu3a_pristine_symm.py'),
    # os.path.join('models', 'alu3a', 'alu3a_pristine_asymm.py'),
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_bot.py'),
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_symm.py'),
    # os.path.join('models', 'alu3a', 'alu3a_central_hole10_asymm.py'),

    # stack 3
    os.path.join('models', 'alu3a', 'alu3a_central_hole15_top.py'),
    os.path.join('models', 'alu3a', 'alu3a_farfield_hole10_top.py'),
    os.path.join('models', 'alu3a', 'alu3a_central_2_hole10_top.py'),
    os.path.join('models', 'alu3a', 'alu3a_crack_45_central_top.py'),

    # randbereich 10 mm
    # 2 löcher 10 mm
    # riss 45 grad 15 mm

    # stack 4


]

# specify the directory on remote machine where GUWlib is located
remote_guwlib_path = '/work/y0106916/GUW_Simulation/GUW/python'

# resources to allocate for the ABAQUS/CAE execution (writing *.INP files)
# acceptable time formats include "minutes", "minutes:seconds", "hours:minutes:seconds", "days-hours",
# "days-hours:minutes" and "days-hours:minutes:seconds"


# bei 16 x 8 und 1 m Platte -> ca. 12 min für ein INP file
cae_n_nodes = 1
cae_n_tasks_per_node = 20
cae_partition = 'standard'
cae_max_time = "3-0:0:0"
# cae_max_time = "0:20:0"

# resources to allocate for each solver run (ABAQUS/Explicit, ABAQUS/Standard)
solver_n_nodes = 1
solver_n_tasks_per_node = 20
solver_partition = 'fat'
solver_max_time = "1-0:0:0"

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
        f"{solver_partition} {solver_max_time} ""False""")
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
