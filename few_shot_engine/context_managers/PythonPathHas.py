import os
from contextlib import contextmanager
from loguru import logger

@contextmanager
def PythonPathHas(pathstr=None):
    
    original_pythonpath = os.environ.get('PYTHONPATH', "")
    try:
        # Append the absolute path to PYTHONPATH
        if pathstr == None:
            logger.warn('PythonPathHas context entered with None: this will still reset the PYTHONPATH on context exit.')
        else:
            abspath = os.path.abspath(pathstr)
            os.environ['PYTHONPATH'] = f"{abspath}{os.pathsep}{original_pythonpath}"
        yield
    finally:
        # Revert PYTHONPATH back to the original
        os.environ['PYTHONPATH'] = original_pythonpath
