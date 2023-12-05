"""
Pipeline to preprocess, setup, solve and post process user defined GUW models.
"""
import os
import subprocess
import textwrap


def submit_model_files(model_file_paths, ):
    """

    :param model_file_paths:
    :return:
    """

    for k, model_file_path in enumerate(model_file_paths):

        # run ABAQUS/CAE on the model.py file to create *.INP file
        model_file_name, _ = os.path.splitext(os.path.basename(model_file_path))
        command = f"abaqus cae noGUI={model_file_path}"
        proc = subprocess.Popen(command, shell=True)
        proc.wait()

        # iterate through all *.INP-files in the simulation directory and generate *.JOB file
        i = 0
        for root, dirs, files in os.walk(os.path.join('results', model_file_name)):
            for file_name in files:
                if file_name.endswith(".inp"):
                    i = i + 1
                    file_name = os.path.splitext(file_name)[0]
                    job_file_path = os.path.join(root, file_name)

                    # generate a SLURM job file
                    generate_abaqus_job_script(output_file_path=job_file_path + '.job',
                                               partition='standard',
                                               n_nodes=1,
                                               n_tasks_per_node=1,
                                               max_time_in_h=1,
                                               slurm_job_name=f'{i}',
                                               inp_file=file_name + '.inp',
                                               working_dir=root)

                    # submit the job
                    command = f"cd {root} && sbatch {file_name}.job"

                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = proc.communicate()

                    if proc.returncode == 0:
                        # Job submission successful, extract the job ID from the output
                        job_id = out.decode().strip().split()[-1]
                        print(f"Job submitted successfully. Job ID: {job_id}")

                        # Now you can use job_id to monitor the log file
                    else:
                        print(f"Job submission failed. Error: {err.decode()}")


def generate_abaqus_job_script(output_file_path, partition, n_nodes, n_tasks_per_node, max_time_in_h, slurm_job_name,
                               inp_file, working_dir):
    """

    Args:
        output_file_path:
        partition:
        n_nodes:
        n_tasks_per_node:
        max_time_in_h:
        slurm_job_name:
        inp_file:
        working_dir:

    Returns:

    """
    content = textwrap.dedent(f"""\
        #!/bin/bash -l

        #SBATCH --partition={partition}
        #SBATCH --nodes={n_nodes}
        #SBATCH --job-name={slurm_job_name}
        #SBATCH --ntasks-per-node={n_tasks_per_node}
        #SBATCH --time={int(max_time_in_h)}:00:00
        #SBATCH -o bo-%j.log

        module purge
        module load software/abaqus/abaqus_2023


        input_file={inp_file}

        working_dir={working_dir}
        cd $working_dir

        ### Create ABAQUS environment file for current job
        env_file=custom_v6.env

        ### Start writing the ABAQUS environment file
        cat << EOF > ${{env_file}}
        mp_file_system = (DETECT,DETECT)
        EOF

        ### Construct a list of hosts and their respective number of CPUs
        node_list=$(scontrol show hostname ${{SLURM_NODELIST}} | sort -u)
        mp_host_list="["
        for host in ${{node_list}}; do
            mp_host_list="${{mp_host_list}}['$host', ${{SLURM_CPUS_ON_NODE}}],"
        done
        mp_host_list=$(echo ${{mp_host_list}} | sed -e "s/,$/]/")

        ### Write hostlist to ABAQUS environment file
        echo "mp_host_list=${{mp_host_list}}"  >> ${{env_file}}


        ### Set input file and job (file prefix) name here
        job_name=${{SLURM_JOB_NAME}}   

        ### Call ABAQUS parallel execution
        abaqus job=${{job_name}} input=${{input_file}} cpus=${{SLURM_NTASKS}} mp_mode=mpi interactive
    """)

    with open(output_file_path, 'w', newline='\n') as file:
        file.write(content)
