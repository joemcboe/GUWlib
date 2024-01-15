from guwlib.functions_cluster.ssh import *
from guwlib.functions_cluster.slurm import *
import re
import ast

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
    # # stash 3 ------------------------------------------------------------------
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
]

working_dir = '/work/y0106916/GitHub_C3D8I/GUW/'

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

# trace back the console output to retrieve the paths of the generated PKL.GZ files
match = re.search(r'\d+', console_output)
job_id = match.group()
cmd = f"cd {working_dir} && tail bo-{job_id}.log"

for attempt in range(20):
    print(f"\nAttempting to tail bo-{job_id}.log in 5 s...")
    time.sleep(5)
    console_output = tail_log_file_with_regex_trigger(username_env_var='tubs_username',
                                                      password_env_var='tubs_password',
                                                      regex_patterns=[r'PKL_PATHS=(\[[^]]*])', 'tail: cannot open'],
                                                      log_file_path=f'{working_dir}bo-{job_id}.log')
    match = re.search(r'PKL_PATHS=(\[[^]]*])', console_output)
    if match:
        break

if match:
    pkl_paths_str = match.group(1)
    pkl_paths_list = ast.literal_eval(pkl_paths_str)
else:
    pkl_paths_list = []

# download every .PKL.GZ file to the local machine
for pkl_file_path in pkl_paths_list:

    print(f'Downloading {pkl_file_path} ...')

    index = pkl_file_path.find('/results/')
    if index != -1:
        local_path = pkl_file_path[index + len('/results/'):]
        local_path = os.path.join('results', os.path.normpath(local_path))
        copy_file_from_remote(remote_path=pkl_file_path,
                              local_path=local_path,
                              username_env_var='tubs_username',
                              password_env_var='tubs_password',
                              hostname='phoenix.hlr.rz.tu-bs.de',
                              port=22)
    else:
        print(f'Failed to download {pkl_file_path}, probably it is not a valid results path.')
