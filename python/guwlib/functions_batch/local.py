import subprocess
import os


def build_and_solve(model_file_paths, n_threads):
    """
    Wrapper to automize the process of building ABAQUS FE model (.INP) files from guwlib model files (.PY) and
    submitting them to the ABAQUS solver on this machine. Results are written to the 'results' directory.

    Subprocess is used to call ABAQUS/CAE and ABAQUS analysis via CLI. Make sure ABAQUS is available (check with
    abaqus information=release).

    :param list[str] model_file_paths: File paths to the guwlib model files (.PY).
    :param int n_threads:  Number of CPUs (physical / virtual) to use for parallel solving in ABAQUS.
    """

    # run ABAQUS/CAE on the model.PY files
    print("Running preprocessing stage (writing .INP files ...)")
    for model_file in model_file_paths:
        print(f"Writing .INP files for {model_file}")
        command = f"abaqus cae noGUI={model_file}"
        proc = subprocess.Popen(command, shell=True)
        proc.wait()

    # find the .INP files and add their file names and paths to a list
    print("Scanning the 'results' directory for the created .INP files ...")
    model_file_names = [os.path.splitext(os.path.basename(model_file_path))[0] for model_file_path in model_file_paths]
    directories_to_search = [os.path.join('results', model_file_name) for model_file_name in model_file_names]
    inp_files = []

    for directory_to_search in directories_to_search:
        for root, dirs, files in os.walk(directory_to_search):
            for file_name in files:
                if file_name.lower().endswith(".inp"):
                    inp_files.append((os.path.abspath(root),
                                      file_name))
    print(f"Found .INP files: {', '.join([inp_file_path[1] for inp_file_path in inp_files])}")

    # run ABAQUS on each of the .inp files
    for inp_file in inp_files:
        job_name = os.path.splitext(inp_file[1])[0]
        job_path = inp_file[0]
        command = f"cd {job_path} & abaqus job={job_name} input={inp_file[1]} cpus={n_threads} interactive"
        print(f"Starting to solve {job_name} on {n_threads} CPUs ...")
        proc = subprocess.Popen(command, shell=True)
        proc.wait()


def extract_results(directories_to_scan=('results', ), data_to_extract='history'):
    """
    Handles automatic batch postprocessing of .ODB files, i.e. extraction of history or field output to NumPy binary
    files (.NPZ) or Pickle files (.PKL, only fallback). The function scans the specified directories for unprocessed
    .ODB files and calls the field / history export helper in ABAQUS/CAE to process the file.

    :param tuple[str] directories_to_scan: directories (including subdirectories) to browse for unprocessed .ODB files
    :param str data_to_extract: type of data to extract ('field' or 'history')
    """
    # find all unprocessed .ODB files in the specified directories
    odb_files = []
    for directory_to_scan in directories_to_scan:
        print(f"Scanning {directory_to_scan} for unprocessed .ODB files ...")
        for root, dirs, files in os.walk(directory_to_scan):
            # convert file names to lowercase for case-insensitive comparison
            lowercase_files = [file.lower() for file in files]

            if any(file.endswith(".odb") for file in lowercase_files) and not \
                    (any(file.endswith(data_to_extract + ".npz") for file in lowercase_files) or
                     any(file.endswith(data_to_extract + ".pkl") for file in lowercase_files)):
                # if directory contains *.odb files but no .pkl or .npz files
                odb_file_paths = [os.path.abspath(root) for file in files if file.lower().endswith(".odb")]
                odb_file_names = [file for file in files if file.lower().endswith(".odb")]
                odb_files.extend([(odb_file_paths[i], odb_file_names[i]) for i, _ in enumerate(odb_file_names)])

    if not odb_files:
        print('No unprocessed files found.')

    # call the export helper script for each of the .ODB files
    processed_files = []
    for odb_file in odb_files:
        odb_file_path = odb_file[0]
        odb_file_name = odb_file[1]

        if data_to_extract == 'history':
            print(f"Extracting the history data for {odb_file_name} ...")
            helper_script_name = os.path.abspath('guwlib/functions_odb/history_export_helper.py')

        elif data_to_extract == 'field':
            print(f"Extracting the history data for {odb_file_name} ...")
            helper_script_name = os.path.abspath('guwlib/functions_odb/field_export_helper.py')

        else:
            raise ValueError('Specify which data to extract. Possible values are: "field" or "history".')

        command = f'cd {odb_file_path} & abaqus cae noGUI={helper_script_name} -- {odb_file_name}'
        proc = subprocess.Popen(command, shell=True)
        proc.wait()
        npz_file = os.path.join(odb_file_path, os.path.splitext(odb_file_name)[0] + '_' + data_to_extract + '.npz')
        pkl_file = os.path.join(odb_file_path, os.path.splitext(odb_file_name)[0] + '_' + data_to_extract + '.pkl')
        if os.path.exists(pkl_file):
            processed_files.append(pkl_file.replace('\\', '\\\\'))
        elif os.path.exists(npz_file):
            processed_files.append(npz_file.replace('\\', '\\\\'))

    if processed_files:
        br = '\n'
        print("Done. The processed files are here:")
        print(br.join(processed_files))

