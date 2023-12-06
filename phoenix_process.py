"""
This script is intended to be run on the Phoenix cluster to
 - create *.INP-files from *.PY files using GUWLIB and ABAQUS/CAE
 - submit the *.INP files as SLURM *.JOB files

Call this script like this:

    `python phoenix_process.py "['models/model_file_1.py', ...]" n_nodes n_tasks_per_node "partition"`

Example usage:

    `python phoenix_process.py "['models/my_model.py', ...]" 2 10 "shortrun_small"`

"""
import os
import sys
import subprocess
import textwrap
import ast


def submit_model_files(model_file_paths, n_nodes, n_tasks_per_node, partition, max_time):
    """

    :param model_file_paths:
    :return:
    """

    print(partition)
    print(max_time)

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
                                               partition=partition,
                                               n_nodes=n_nodes,
                                               n_tasks_per_node=n_tasks_per_node,
                                               max_time_in_h=max_time,
                                               slurm_job_name=f'{k}_{i}',
                                               inp_file=file_name + '.inp',
                                               working_dir=root)

                    # submit the job
                    command = f"cd {root} && sbatch {file_name}.job"

                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = proc.communicate()

                    if proc.returncode == 0:
                        # Job submission successful, extract the job ID from the output
                        job_id = out.decode().strip().split()[-1]
                        print(f"Submitted. JOB_ID={job_id}")

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
        module load software/abaqus/abaqus_2019


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


if __name__ == "__main__":

    script_name = sys.argv[0]
    arguments = sys.argv[1:]

    # Extracting specific arguments based on their positions in the list
    model_file_paths_str = arguments[0] if arguments else "[]"
    n_nodes = int(arguments[1]) if len(arguments) > 1 else 1
    n_tasks_per_node = int(arguments[2]) if len(arguments) > 2 else 1
    partition = arguments[3] if len(arguments) > 3 else 'standard'
    max_time = int(arguments[4]) if len(arguments) > 4 else 12

    # Parsing the string representation of a list into an actual list
    model_file_paths = ast.literal_eval(model_file_paths_str)

    if model_file_paths is not None:
        submit_model_files(model_file_paths=model_file_paths, n_nodes=n_nodes, n_tasks_per_node=n_tasks_per_node,
                           partition=partition, max_time=max_time)
