"""
This script is intended to be run on the Phoenix cluster to extract the history data from ODB files, written by the
Abaqus Solver.

Call this script like this:

    `python phoenix_post_process.py "['results/my_model', ...]"

"""
import os
import sys
import subprocess
import ast


def extract_history_from_output_databases(results_folders):
    """

    :param results_folders:
    :return:
    """

    helper_script_name = os.path.join('guwlib', 'functions_odb', 'abaqus_odb_history_export_helper.py')
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

    :param directory:
    :return:
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
        print("PKL_PATHS=".format(pkl_paths))

