from contextlib import AbstractContextManager
from context_managers.CatchingContextManager import CatchingContextManager
import json
from typing import Union, Callable

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
        self.cm = CatchingContextManager(open, self.args, self.error_dict)

    def __enter__(self):
        self.f = self.cm.__enter__()
        return self.f

    def __exit__(self, exc_type, exc_value, traceback):
        return self.cm.__exit__(exc_type, exc_value, traceback)