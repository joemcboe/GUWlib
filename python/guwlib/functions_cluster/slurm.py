import textwrap


def generate_slurm_job_for_abaqus_solver(output_file_path, partition, n_nodes, n_tasks_per_node, max_time, slurm_job_name,
                                         inp_file, working_dir):
    """
    Generates a SLURM job script (*.JOB) for running the ABAQUS 2019 solver on the provided .INP file.

    :param str output_file_path: Path to the generated SLURM .JOB script file.
    :param str partition: Name of the SLURM partition to allocate resources from (e.g. 'standard', 'shortrun_small').
    :param int n_nodes: Number of compute nodes to request for the job.
    :param int n_tasks_per_node: Number of tasks (CPU processes) to allocate per node.
    :param str max_time: Maximum time for the job to run before being cancelled.
    :param str slurm_job_name: Name of the SLURM job.
    :param str inp_file: Path to the ABAQUS input (.INP) file.
    :param str working_dir: Working directory where the job will be executed.

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


def generate_slurm_job(output_file_path, partition, n_nodes, n_tasks_per_node, max_time, slurm_job_name,
                       command, working_dir, modules_to_load=('software/abaqus/abaqus_2019',)):
    """
    Generates a SLURM job script (*.JOB) that loads the specified modules and executes the provided command.

    :param str output_file_path: Path to the generated SLURM .JOB script file.
    :param str partition: Name of the SLURM partition to allocate resources from (e.g. 'standard', 'shortrun_small').
    :param int n_nodes: Number of compute nodes to request for the job.
    :param int n_tasks_per_node: Number of tasks (CPU processes) to allocate per node.
    :param str max_time: Maximum time for the job to run before being cancelled.
    :param str slurm_job_name: Name of the SLURM job.
    :param str working_dir: Working directory where the job will be executed.
    :param str command: Command to run.
    :param tuple[str] modules_to_load: Modules to load from Environment Modules manager.
    :param str working_dir: Working directory where the job will be executed.

    :return: None
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
