from guwlib.functions_cluster.ssh import *
from guwlib.functions_cluster.slurm import *
import re
import ast

"""
This script automates the download of ABAQUS results (.ODB files) from a remote PC. 

- call the cluster_post.py on the remote machine with directories to scan as argument
- wait for the job to finish
"""


# parameters set by the user -------------------------------------------------------------------------------------------
# specify the model files for which to download the results (only the model name is required)

model_files_local = [
    os.path.join('models', 'convergence_pristine_20_x_10.py')
]

working_dir = '/beegfs/work/y0106916/GUW_Simulation/GUW/python'

# ----------------------------------------------------------------------------------------------------------------------
# compile a list of result folders from the script names
result_directories = [f"'results/{os.path.splitext(os.path.basename(model_file_path))[0]}'"
                      for model_file_path in model_files_local]
args = '"[' + ', '.join(result_directories) + ']"'

# for each result directory, download the converted_files.txt

# for each line in the converted_files.txt, extract the remote paths and add them to a list
with open(file_path, 'r') as file:
    for line in file:
        # Strip any leading or trailing whitespaces and append to the list
        file_paths.append(line.strip())

# for each file in the list, download the file from the file path from src to dst
# dst is a directory on the local computer



