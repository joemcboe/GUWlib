"""
Example script on how to batch-process multiple model files (building, solving and exporting data) on a remote
machine (LINUX with SLURM installed, e.g. PHOENIX HPC Cluster).

:Usage:
    1. Specify the paths to the GUWlib model files (.PY) in the 'model_file_paths' list.
    2. Run the script, calling the respective functions for pre- and postprocessing.
"""
from guwlib.functions_batch.remote import *

# path to the remote location of GUWlib
remote_guwlib_path = '/beegfs/work/y0106916/GUW_UNIT_TEST/GUW/python'
preprocessing = True
postprocessing = False
download = False

# preprocessing and solving -------------------------------------------------------------------------------------------+
if preprocessing:
    # model files (.PY) to process
    model_file_paths = ['models/unit_tests/test02.py', ]

    # SLURM parameters for preprocessing, solving, and postprocessing
    # parameters for preprocessing apply to all models, make sure that the total time (max_time) is sufficient
    slurm_preprocessing = {"n_nodes": 1,
                           "n_tasks_per_node": 2,
                           "partition": "standard",
                           "max_time": "0:5:0"}

    # parameters apply to the solving process of one simulation each
    slurm_solving = {"n_nodes": 1,
                     "n_tasks_per_node": 10,
                     "partition": "standard",
                     "max_time": "0:5:0"}

    # call the batch function to upload the model files, initiate automated preprocessing and solving
    build_and_solve(model_files_local=model_file_paths,
                    remote_guwlib_path=remote_guwlib_path,
                    cae_slurm_settings=slurm_preprocessing,
                    solver_slurm_settings=slurm_solving,
                    hostname='phoenix.hlr.rz.tu-bs.de', port=22)

# postprocessing ------------------------------------------------------------------------------------------------------+
if postprocessing:
    # parameters apply to the extraction process of one .ODB file each
    slurm_postprocessing = {"n_nodes": 1,
                            "n_tasks_per_node": 10,
                            "partition": "standard",
                            "max_time": "0:15:0"}

    # remote location where to look for .ODB files that are ready for results extraction
    directories_to_scan = ['results/model_02_one_lc/',]

    # call the batch function for automated result export
    extract_results(directories_to_scan=directories_to_scan, data_to_extract='history',
                    remote_guwlib_path=remote_guwlib_path, cae_slurm_settings=slurm_postprocessing,
                    max_parallel_cae_instances=5, hostname='phoenix.hlr.rz.tu-bs.de', port=22)
    print("Make sure to check the status of your current post-processing job and download the results"
          "after it has finished.")


# downloading results -------------------------------------------------------------------------------------------------+
if download:
    download_results(remote_guwlib_path=remote_guwlib_path, hostname='phoenix.hlr.rz.tu-bs.de', port=22)

