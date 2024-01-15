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
    os.path.join('models', 'testing', 'small_model.py'),
]

# specify the number of threads to use for the solver run (ABAQUS/EXPLICIT)
n_threads = 1

# ----------------------------------------------------------------------------------------------------------------------
# run ABAQUS/CAE on the model.py files
print("Running preprocessing stage (writing .INP files ...)")
for model_file in model_files_local:
    print(f"Writing .INP files for {model_file}")
    command = f"abaqus cae noGUI={model_file}"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()

# find the .inp files and add their file paths to a list
print("Scanning the 'results' directory for the created .INP files ...")
for model_file in model_files_local:
    pass


# call the solver for each of the .inp files


