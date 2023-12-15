"""
This script opens the ABAQUS/CAE environment to preview a GUWLIB model file (.PY). Specify
the path to the model file, and the script will execute Abaqus/CAE to display the model.

Usage:
    1. Specify the path to the GUWLIB model file in the 'model_file' variable.
    2. Run the script.

Example:
    python.exe model_preview.py

Note:
    The .INP file generation in ABAQUS/CAE is omitted when Abaqus is run in GUI mode.
"""

import subprocess
import os

# specify your model file path here
model_file = os.path.join('models/convergence_test', 'convergence_pristine_20_x_10.py')


# run ABAQUS/CAE on the model.py file ----------------
command = f"abaqus cae script={model_file}"
proc = subprocess.Popen(command, shell=True)
proc.wait()
