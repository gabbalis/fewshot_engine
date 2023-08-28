import sys
import subprocess
from context_managers.PythonPathHas import PythonPathHas

command = "python .\\src\\zip_utils.py --unzipped_dir .\\test\\test_unziped_dir\\ --zipped_file .\\test\\test_zipped.json --zip"

with PythonPathHas('.'):
    subprocess.run(command, shell=True)
