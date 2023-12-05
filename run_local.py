import subprocess

model_file = 'models/example_01_point_force_isotropic.py'

# run ABAQUS/CAE on the model.py file
command = f"abaqus cae script={model_file}"
proc = subprocess.Popen(command, shell=True)
proc.wait()
