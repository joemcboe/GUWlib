"""
Pipeline to preprocess, setup, solve and post process user defined GUW models.
"""
import os
import subprocess
import guwlib.functions_phoenix.slurm as slurm

model_file_paths = \
    [
        os.path.join("models", "example_01_point_force_isotropic.py"),
    ]

for k, model_file_path in enumerate(model_file_paths):

    # run ABAQUS/CAE on the model.py file to create *.INP file
    model_file_name, _ = os.path.splitext(os.path.basename(model_file_path))
    command = f"abaqus cae noGUI={model_file_path}"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()

    # Iterate through all *.INP-files in the simulation directory and generate a *.JOB file
    i = 0
    for root, dirs, files in os.walk(os.path.join('results', model_file_name)):
        for file_name in files:
            if file_name.endswith(".inp"):
                i = i + 1
                file_path = os.path.join(root, file_name)
                job_file_path = os.path.join(root, os.path.splitext(file_name)[0])

                # generate a job file for slurm
                slurm.generate_abaqus_job_script(output_file_path=job_file_path+'.job',
                                                 partition='standard',
                                                 n_nodes=1,
                                                 n_tasks_per_node=1,
                                                 max_time_in_h=1,
                                                 slurm_job_name=f'{i}',
                                                 inp_file=file_name,
                                                 working_dir='')

                # submit the job
                command = f"cd {root} && sbatch {file_name}"
                proc = subprocess.Popen(command, shell=True)
                proc.wait()
