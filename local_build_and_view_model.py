import subprocess

model_file = 'models/convergence_test/convergence_pristine_4_x_1.py'

# run ABAQUS/CAE on the model.py file
command = f"abaqus cae script={model_file}"
proc = subprocess.Popen(command, shell=True)
proc.wait()
