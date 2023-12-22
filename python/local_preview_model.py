"""
This script opens the ABAQUS/CAE environment to preview a GUWlib model file (*.PY). Specify
the path to the model file, and the script will execute Abaqus/CAE to display the model. The
generation of .INP files in ABAQUS/CAE is omitted when Abaqus is run in GUI mode.

:Usage:
    1. Specify the path to the GUWlib model file in the 'model_file' variable.
    2. Run the script.
"""

import subprocess
import os

# specify your model file path here
model_file = os.path.join('models/examples', 'example_02.py')


# run ABAQUS/CAE on the model.py file ----------------
command = f"abaqus cae script={model_file}"
proc = subprocess.Popen(command, shell=True)
proc.wait()
