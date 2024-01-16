"""
This script ...

:Usage:
    1. Specify the path to the GUWlib model file in the 'model_file' variable.
    2. Run the script.
"""

import subprocess
import os


# parameters set by the user -------------------------------------------------------------------------------------------
# specify the model files to build and solve on this machine
model_files_local = [
    os.path.join('models', 'testing', 'small_a.py'),
]

# specify the number of threads to use for the solver run (ABAQUS/EXPLICIT)
n_threads = 1

# ---------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                                                                                                                      #
#                                     !DO NOT CHANGE THE FOLLOWING SECTIONS!                                           #
#                                                                                                                      #
#                                                                                                                      #
# ---------------------------------------------------------------------------------------------------------------------#

# run ABAQUS/CAE on the model.py files
print("Running preprocessing stage (writing .INP files ...)")
for model_file in model_files_local:
    print(f"Writing .INP files for {model_file}")
    command = f"abaqus cae noGUI={model_file}"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()

# find the .inp files and add their file names and paths to a list
print("Scanning the 'results' directory for the created .INP files ...")
inp_files = []
directory_to_search = 'results'
for model_file in model_files_local:
    for root, dirs, files in os.walk(directory_to_search):
        for file_name in files:
            if file_name.lower().endswith(".inp"):
                inp_files.append((os.path.abspath(root),
                                  file_name))
print(f"Found .INP files: {', '.join([inp_file_path[1] for inp_file_path in inp_files])}")


# run ABAQUS on each of the .inp files
for inp_file in inp_files:
    job_name = os.path.splitext(inp_file[1])[0]
    job_path = inp_file[0]
    command = f"cd {job_path} & abaqus job={job_name} input={inp_file[1]} cpus={n_threads} interactive"
    print(f"Starting to solve {job_name} on {n_threads} CPUs ...")
    proc = subprocess.Popen(command, shell=True)
    proc.wait()
