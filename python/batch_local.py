"""
Example script on how to batch-process multiple model files (.PY), i.e. building, solving and exporting data on the
local machine using batch helper functions.

:Usage:
    1. Specify the paths to the GUWlib model files (.PY) in the 'model_file_paths' list.
    2. Run the script, calling the respective functions for pre- and postprocessing.
"""
from guwlib.functions_batch.local import *

# define your GUWlib model files (.PY) here ---------------------------------------------------------------------------+
model_file_paths = ['models/unit_tests/test02.py', ]


# (preprocessing and submitting) call the batch function for automated building and solving of the models -------------+
build_and_solve(model_file_paths=model_file_paths,
                n_threads=2)


# (postprocessing) call the batch function for automated result export ------------------------------------------------+
extract_results(directories_to_scan=('results',),
                data_to_extract='history')
