"""
This script ...

... it will search for .ODB files in the 'results' directory.

:Usage:
    1. Specify the path to the GUWlib model file in the 'model_file' variable.
    2. Run the script.
"""

import subprocess
import os


# parameters set by the user -------------------------------------------------------------------------------------------
# specify the model files for which to extract the results on this machine

model_files_local = [
    os.path.join('models', 'testing', 'small_model.py'),
]

extract_data = 'history'


# ---------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                                                                                                                      #
#                                     !DO NOT CHANGE THE FOLLOWING SECTIONS!                                           #
#                                                                                                                      #
#                                                                                                                      #
# ---------------------------------------------------------------------------------------------------------------------#

# run ABAQUS/CAE on the model.py files
print("Scanning the 'results' directory for unprocessed .ODB files ...")
odb_files = []
directory_to_search = 'results'
for model_file in model_files_local:
    for root, dirs, files in os.walk(directory_to_search):
        # convert file names to lowercase for case-insensitive comparison
        lowercase_files = [file.lower() for file in files]

        if any(file.endswith(".odb") for file in lowercase_files) and not any(
                file.endswith(".npz") for file in lowercase_files):
            # if directory contains *.odb files but no *.pkl.gz files
            odb_file_paths = [os.path.abspath(root) for file in files if file.lower().endswith(".odb")]
            odb_file_names = [file for file in files if file.lower().endswith(".odb")]
            odb_files.extend([(odb_file_paths[i], odb_file_names[i]) for i, _ in enumerate(odb_file_names)])

if not odb_files:
    print('No unprocessed files found.')

# call the export helper script for each of the .ODB files
npz_files = []
for odb_file in odb_files:
    odb_file_path = odb_file[0]
    odb_file_name = odb_file[1]

    if extract_data == 'history':
        print(f"Extracting the history data for {odb_file_name} ...")
        helper_script_name = os.path.abspath('guwlib/functions_odb/history_export_helper.py')
        command = f'cd {odb_file_path} & abaqus cae noGUI={helper_script_name} -- {odb_file_name}'
        proc = subprocess.Popen(command, shell=True)
        proc.wait()
        npz_file = os.path.join(odb_file_path, os.path.splitext(odb_file_name)[0] + '.npz')
        npz_files.append(npz_file.replace('\\', '\\\\'))

    if extract_data == 'field':
        raise NotImplementedError('Field export helper is not yet implemented.')

if npz_files:
    br = '\n'
    print("Done. The processed NPZ files are here:")
    print(br.join(npz_files))
