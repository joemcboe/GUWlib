from guwlib.functions_cluster.ssh import *
from guwlib.functions_cluster.slurm import *
import re
import ast

"""
This script automates the download of ABAQUS results (.ODB files) from a remote PC. 

"""


# parameters set by the user -------------------------------------------------------------------------------------------
# specify the working directory here, in which a txt file should be

working_dir = '/beegfs/work/y0106916/GUW_2024/GUW/python'

# ---------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                                                                                                                      #
#                                     !DO NOT CHANGE THE FOLLOWING SECTIONS!                                           #
#                                                                                                                      #
#                                                                                                                      #
# ---------------------------------------------------------------------------------------------------------------------#


# download the converted_files.txt
list_txt_file = 'converted_odb_files.txt'
try:
    copy_file_from_remote(remote_path=f'{working_dir}/{list_txt_file}',
                          local_path=f'{list_txt_file}',
                          username_env_var='tubs_un',
                          password_env_var='tubs_pw')

except FileNotFoundError:
    print(f"File {working_dir}/{list_txt_file} is not available on the remote machine. Make"
          f"sure that you specified the correct working_dir and that you have already extracted"
          f"results to .NPZ files. This script is for downloading only.")


# for each line in the converted_files.txt, extract the remote paths and add them to a list
file_paths = []
with open(list_txt_file, 'r') as file:
    for line in file:
        file_paths.append(line.strip())

# for each file in the list, download the file from the file path from src to dst
for file_path in file_paths:
    # when copying the remote files to the local machine, flatten the directory out by one layer
    file_name = os.path.basename(file_path)
    parent_directory = os.path.dirname(os.path.dirname(file_path))
    local_path = os.path.join(parent_directory, file_name)
    copy_file_from_remote(remote_path=f'{working_dir}/{file_path}',
                          local_path=local_path,
                          username_env_var='tubs_un',
                          password_env_var='tubs_pw')
    print(f"Copied {file_name} to {parent_directory}/.")




