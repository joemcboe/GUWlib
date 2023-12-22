"""
This script is designed to be executed on the Phoenix cluster and intended for post-processing Abaqus
simulation results  by extracting history data from output database (.ODB) files. It utilizes a helper
script, 'abaqus_odb_history_export_helper.py', to perform the extraction. The script processes each output
database (.ODB) file in the specified directories, extracts history data, and saves the processed data as
compressed pickle files (.PKL.GZ).

If executed as a standalone script, it accepts a list of result directories as a command-line argument, performs
the extraction, and prints the paths to the generated compressed pickle files.

Usage:
    python abaqus_post_process.py "<results_dir_paths>"

Arguments:
    - results_dir_paths (str): A string representation of a Python list containing paths to directories
      containing Abaqus simulation result files (.ODB). Enclose the list in quotes, e.g.,
      "['/path/to/results/folder1', '/path/to/results/folder2']".

Example:
    python abaqus_post_process.py "['/path/to/results/folder1', '/path/to/results/folder2']"

Note: ABAQUS software must be installed, and the script assumes a configured SLURM environment for proper execution.
"""

import os
import sys
import subprocess
import ast


def extract_history_from_output_databases(results_folders):
    """
    Scans the specified results folders for ABAQUS output database files (.ODB), extracts the history data
    and saves it as NumPy .NPZ files in the same directory as the .ODB file. The file paths to the .NPZ files
    are returned.

    :param List[str] results_folders: paths to directories containing Abaqus output database files (.ODB).
    :return: List[str], paths to the extracted history data files in NumPy .NPZ format.

    Example:
    extract_history_from_output_databases(['/path/to/results/folder1', '/path/to/results/folder2'])

    Note: ABAQUS software must be installed, and the helper script 'abaqus_odb_history_export_helper.py' is
    expected to be located in the 'guwlib/functions_odb/' directory.
    """

    helper_script_name = os.path.join('..', 'functions_odb', 'abaqus_odb_history_export_helper.py')
    extracted_data_file_names = []

    for result_folder in results_folders:

        # find the odb file paths
        odb_files = find_odb_files(result_folder)

        for odb_file in odb_files:

            # process the odb file
            extracted_data_file_name = f'{os.path.dirname(odb_file)}_history'
            cmd = f'abaqus cae noGUI={helper_script_name} -- "{odb_file}" "{extracted_data_file_name}"'
            proc = subprocess.Popen(cmd, shell=True)
            proc.wait()
            extracted_data_file_name_abs_path = os.path.abspath(f'{extracted_data_file_name}.pkl.gz')
            extracted_data_file_names.append(extracted_data_file_name_abs_path)

    return extracted_data_file_names


def find_odb_files(directory):
    """
    Find all Abaqus output database files (.ODB) in the specified directory.

    :param directory: str, path to the directory to search for .ODB files.
    :return: List[str], paths to the located .ODB files.

    Example:
    find_odb_files('/path/to/results/folder')

    """
    odb_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".odb"):
                odb_files.append(os.path.join(root, file))
    return odb_files


if __name__ == "__main__":

    script_name = sys.argv[0]
    arguments = sys.argv[1:]

    # Extracting specific arguments based on their positions in the list
    results_dir_paths_str = arguments[0] if arguments else "[]"

    # Parsing the string representation of a list into an actual list
    results_dir_paths = ast.literal_eval(results_dir_paths_str)

    if results_dir_paths is not None:
        pkl_paths = extract_history_from_output_databases(results_folders=results_dir_paths)
        print("PKL_PATHS={}".format(pkl_paths))

