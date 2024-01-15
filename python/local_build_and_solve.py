"""
This script opens the ABAQUS/CAE GUI to preview a GUWlib model file (.PY). Specify the
path to the model file, and the script will execute Abaqus/CAE to display the model. The
generation of .INP files in ABAQUS/CAE is omitted when Abaqus is run in GUI mode.

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
    command = f"abaqus cae script={model_file}"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()

# find the .inp files and add their file path and file name to a list


# call the solver for each of the .inp files


