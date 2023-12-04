"""
Pipeline to preprocess, setup, solve and postprocess user defined GUW models.
"""
import os
import subprocess

model_file_paths = \
    [
        os.path.join("models", "example_01_point_force_isotropic.py"),
    ]

for model_file in model_file_paths:

    # run ABAQUS/CAE on the model.py file to create *.INP file
    command = f"abaqus cae script={model_file}"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()
