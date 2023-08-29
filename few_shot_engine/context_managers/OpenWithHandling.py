from contextlib import AbstractContextManager
from .CatchingContextManager import CatchingContextManager
import json
from typing import Union, Callable
from loguru import logger
import os

class OpenWithHandling(AbstractContextManager):
    def __init__(self, 
                 file: Union[str, bytes, int], 
                 mode: str = 'r',
                 buffering: int = -1,
                 encoding: Union[str, None] = None,
                 errors: Union[str, None] = None,
                 newline: Union[str, None] = None,
                 closefd: bool = True,
                 opener: Union[Callable, None] = None):
        
        self.args = {
            'file': file,
            'mode': mode,
            'buffering': buffering,
            'encoding': encoding,
            'errors': errors,
            'newline': newline,
            'closefd': closefd,
            'opener': opener
        }
        self.error_dict = {
            json.JSONDecodeError: "JSON decode error: {e} while parsing {file}",
            FileNotFoundError: "File {file} not found.",
            Exception: "An unexpected {error_type} occurred with {file} open: {e}"
        }
        self.cm = CatchingContextManager(self._ensure_directory_and_open, self.args, self.error_dict)

    # Helper function to make sure the directory exists and warn if it doesn't
    def _ensure_directory_and_open(self, *args, **kwargs):
        file_path = kwargs.get('file', None) or args[0]
        directory = os.path.dirname(file_path)
        
        # Create directory if it does not exist
        if not os.path.exists(directory):
            logger.warning(f"Directory {directory} did not exist; creating it.")
            os.makedirs(directory)
        
        # Call the actual open function
        return open(*args, **kwargs)

        

    def __enter__(self):
        self.f = self.cm.__enter__()
        return self.f

    def __exit__(self, exc_type, exc_value, traceback):
        return self.cm.__exit__(exc_type, exc_value, traceback)