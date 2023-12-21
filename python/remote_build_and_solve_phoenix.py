"""

"""




from guwlib.functions_phoenix.ssh import *
from guwlib.functions_phoenix.slurm import *

# parameters set by the user -------------------------------------------------------------------------------------------
# specify the model files to upload to the cluster
model_files_local = [
    os.path.join('models/convergence_test', 'convergence_pristine_20_x_10.py')
    # C3D8R stashes -----------------------------------------------------------
    # os.path.join('models/convergence_test', 'convergence_pristine_10_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_10_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_10_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_10_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_15_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_15_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_15_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_15_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_20_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_20_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_20_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_20_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_25_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_25_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_25_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_25_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_8.py'),
    # stash 2 -------------------------------------------------------------------
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_10_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_10_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_15_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_15_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_20_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_20_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_25_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_25_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_12.py'),
    # stash 3 ------------------------------------------------------------------
    # os.path.join('models/convergence_test', 'convergence_defect_20_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_20_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_20_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_20_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_20_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_20_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_25_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_25_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_25_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_25_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_25_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_25_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_2.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_4.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_6.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_8.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_10.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_12.py')
    # stash 4 -----------------------------------------------------------------------------
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_12.py')
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_14.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_30_x_16.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_14.py'),
    # os.path.join('models/convergence_test', 'convergence_defect_35_x_16.py'),
    #
    # # os.path.join('models/convergence_test', 'convergence_pristine_30_x_12.py')
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_14.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_30_x_16.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_12.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_14.py'),
    # os.path.join('models/convergence_test', 'convergence_pristine_35_x_16.py'),
]

# nodes, tasks, partition to use for the actual ABAQUS/Explicit execution
n_nodes = 1
n_tasks_per_node = 10
partition = 'shortrun_small'
max_time = 10

# ----------------------------------------------------------------------------------------------------------------------
# copy the model files to the cluster
for model_file in model_files_local:
    file_name = os.path.basename(model_file)
    remote_path = f'/work/y0106916/GitHub_C3D8I/GUW/models/{file_name}'
    copy_file_to_remote(model_file, remote_path, 'tubs_username', 'tubs_password')
    print(f'Copied {file_name} to Phoenix.')

# generate a job file that can call phoenix_process.py on the cluster --------------------------------------------------
model_files_remote = ('"[' +
                      ", ".join(["'models/{}'".format(os.path.basename(model_file))
                                 for model_file in model_files_local])
                      + ']"')
args = f"{model_files_remote} {int(n_nodes)} {int(n_tasks_per_node)} {partition} {max_time}"
working_dir = '/work/y0106916/GitHub_C3D8I/GUW/'
job_file_name = 'temp.job'
generate_python_job_script(output_file_path=job_file_name,
                           partition='standard',
                           n_nodes=1,
                           n_tasks_per_node=20,
                           max_time_in_h=2,
                           slurm_job_name='master',
                           python_file='phoenix_process.py',
                           args=args,
                           working_dir=working_dir)

# copy the master JOB file to the remote and run it --------------------------------------------------------------------
copy_file_to_remote(job_file_name, f'{working_dir}/{job_file_name}',
                    'tubs_username', 'tubs_password')
cmd = f'cd {working_dir} && sbatch {job_file_name}'
run_commands_on_remote(command=cmd, username_env_var='tubs_username', password_env_var='tubs_password')

# tail the jobs in one console each ------------------------------------------------------------------------------------
for model_file in model_files_local:
    pass
