import time

from guwlib.functions_phoenix.ssh import *
from guwlib.functions_phoenix.slurm import *
import re

# specify the model files to upload to the cluster
model_files_local = [
    os.path.join('models/convergence_test', 'convergence_pristine_10_x_2.py'),
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
]

working_dir = '/work/y0106916/GitHub2/GUW/'

# ----------------------------------------------------------------------------------------------------------------------

# compile a list of result folders from the script names
result_directories = [f"'results/{os.path.splitext(os.path.basename(model_file_path))[0]}'"
                      for model_file_path in model_files_local]
args = '"[' + ', '.join(result_directories) + ']"'
print(args)

# generate a job file
job_file_name = 'temp.job'
generate_python_job_script(output_file_path=job_file_name,
                           partition='standard',
                           n_nodes=1,
                           n_tasks_per_node=1,
                           max_time_in_h=2,
                           slurm_job_name='collect',
                           python_file='phoenix_post_process.py',
                           args=args,
                           working_dir=working_dir)

# call the job file on the cluster
copy_file_to_remote(job_file_name, f'{working_dir}/{job_file_name}',
                    'tubs_username', 'tubs_password')
cmd = f'cd {working_dir} && sbatch {job_file_name}'
console_output = run_commands_on_remote(command=cmd, username_env_var='tubs_username', password_env_var='tubs_password')

match = re.search(r'\d+', console_output)
job_id = match.group()

cmd = f"cd {working_dir} && tail bo-{job_id}.log"
time.sleep(5)
pkl_paths = run_command_with_output_trigger(command=cmd,
                                            username_env_var='tubs_username',
                                            password_env_var='tubs_password',
                                            trigger_string='PKL_PATHS=')
print(pkl_paths)

# receive the list of PKL-GZ files
# download to the local computer
