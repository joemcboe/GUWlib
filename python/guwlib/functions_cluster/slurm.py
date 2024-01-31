import textwrap


def generate_abaqus_solver_job_script(output_file_path, partition, n_nodes, n_tasks_per_node, max_time, slurm_job_name,
                                      inp_file, working_dir):
    """
    Generates a SLURM job script (*.JOB) for running the ABAQUS 2019 solver on the provided .INP file.

    The function generates a SLURM job script (*.JOB) with the specified parameters. It includes SLURM directives for
    partition, number of nodes, job name, tasks per node, and maximum time. The SLURM job loads the ABAQUS_2019
    software module, sets up the ABAQUS environment file, and executes the ABAQUS job.

    :param str output_file_path: path to the output SLURM job script file.
    :param str partition: name of the SLURM partition to allocate resources from.
    :param int n_nodes: int, number of compute nodes to request for the job.
    :param int n_tasks_per_node: number of tasks (CPU cores) to allocate per node.
    :param int max_time: maximum time for the job to run before being cancelled.
    :param str slurm_job_name: name of the SLURM job.
    :param str inp_file: path to the ABAQUS input (.INP) file.
    :param str working_dir: working directory where the job will be executed.

    :return: None
    """
    content = textwrap.dedent(f"""\
        #!/bin/bash -l

        #SBATCH --partition={partition}
        #SBATCH --nodes={n_nodes}
        #SBATCH --job-name={slurm_job_name}
        #SBATCH --ntasks-per-node={n_tasks_per_node}
        #SBATCH --time={max_time}
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


def generate_command_job_script(output_file_path, partition, n_nodes, n_tasks_per_node, max_time, slurm_job_name,
                                command, working_dir, modules_to_load=('software/abaqus/abaqus_2019',)):
    """
    Generates a SLURM job script (*.JOB) for running a command script on an HPC cluster (e.g. Phoenix cluster).

    :param str, output_file_path: path to the output SLURM job script file.
    :param str, partition: name of the SLURM partition to allocate resources from.
    :param int, n_nodes: number of compute nodes to request for the job.
    :param int, n_tasks_per_node: number of tasks (CPU cores) to allocate per node.
    :param int, max_time: maximum time for the job to run.
    :param str, slurm_job_name: name of the SLURM job file.
    :param str, command: command to run.
    :param list[str], modules_to_load: modules that SLURM should load.
    :param str, working_dir: working directory where the job will be executed.

    :return: None

    The function generates a SLURM job script with the specified parameters. It includes SLURM directives for
    partition, number of nodes, job name, tasks per node, and maximum time. It loads the ABAQUS_2019 and
    Python software modules, sets the working directory, and executes the specified Python script with the
    provided command-line arguments.
    """
    modules_to_load = "\n".join(["module load " + module for module in modules_to_load])
    content = textwrap.dedent(f"""\
        #!/bin/bash -l

        #SBATCH --partition={partition}
        #SBATCH --nodes={n_nodes}
        #SBATCH --job-name={slurm_job_name}
        #SBATCH --ntasks-per-node={n_tasks_per_node}
        #SBATCH --time={max_time}
        #SBATCH -o bo-%j.log

        module purge
        {modules_to_load}

        working_dir={working_dir}
        cd $working_dir
        {command}

    """)

    with open(output_file_path, 'w', newline='\n') as file:
        file.write(content)


# -> remote_build_and_solve
# -> remote_extract_results
# def generate_python_job_script(output_file_path, partition, n_nodes, n_tasks_per_node, max_time, slurm_job_name,
#                                python_file, args, working_dir):
#     """
#     Generates a SLURM job script (*.JOB) for running a Python script .
#
#     :param str, output_file_path: path to the output SLURM job script file.
#     :param str, partition: name of the SLURM partition to allocate resources from.
#     :param int, n_nodes: number of compute nodes to request for the job.
#     :param int, n_tasks_per_node: number of tasks (CPU cores) to allocate per node.
#     :param int, max_time: maximum time for the job to run.
#     :param str, slurm_job_name: name of the SLURM job file.
#     :param str, python_file: path to the Python script to be executed.
#     :param str, args: command-line arguments to pass to the Python script.
#     :param str, working_dir: working directory where the job will be executed.
#
#     :return: None
#
#     The function generates a SLURM job script with the specified parameters. It includes SLURM directives for
#     partition, number of nodes, job name, tasks per node, and maximum time. It loads the ABAQUS_2019 and
#     Python software modules, sets the working directory, and executes the specified Python script with the
#     provided command-line arguments.
#     """
#
#     content = textwrap.dedent(f"""\
#         #!/bin/bash -l
#
#         #SBATCH --partition={partition}
#         #SBATCH --nodes={n_nodes}
#         #SBATCH --job-name={slurm_job_name}
#         #SBATCH --ntasks-per-node={n_tasks_per_node}
#         #SBATCH --time={max_time}
#         #SBATCH -o bo-%j.log
#
#         module purge
#         module load software/abaqus/abaqus_2019
#         module load python/3.9.7
#
#         working_dir={working_dir}
#         cd $working_dir
#         python3.9 {python_file} {args}
#
#     """)
#
#     with open(output_file_path, 'w', newline='\n') as file:
#         file.write(content)
