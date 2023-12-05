import textwrap


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


def generate_python_job_script(output_file_path, partition, n_nodes, n_tasks_per_node, max_time_in_h, slurm_job_name,
                               python_file, args, working_dir):

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
        module load python/3.9.7

        working_dir={working_dir}
        cd $working_dir
        python3.9 {python_file} {args}
        
    """)

    with open(output_file_path, 'w', newline='\n') as file:
        file.write(content)
