from contextlib import AbstractContextManager
from loguru import logger
import sys

# TODO context managers and better coding norms for loguru
from loguru import logger
# Loguru setup
logger.remove()
logger.add(sys.stderr, format="<green>{time}</green> <level>{message}</level>", colorize=True, level="INFO")

def colorize_args(args, extra_args, color_map):
    colored_args = {}
    for key, value in {**args, **extra_args}.items():
        color_code = color_map.get(key, "\033[0m")  # Get color code for the key or default to reset color
        end_color = "\033[0m"
        colored_args[key] = f"{color_code}{value}{end_color}"
    return colored_args

def my_custom_error(error_string, args, extra_args):
    color_map = {
        'file': "\033[36m",  # Cyan
        'e': "\033[31m",     # Red
        # Add more mappings here if needed
    }
    colored_args = colorize_args(args, extra_args, color_map)
    logger.error(error_string.format(**colored_args))
# TODO also a library for them so they don't live like... here?


class CatchingContextManager(AbstractContextManager):
    def __init__(self, cm, args, error_dict):
        self.cm = cm
        self.args = args
        self.error_dict = error_dict

    def __enter__(self):
        self.thing = self.cm(**self.args)
        return self.thing.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        for error_type in self.error_dict.keys():
            if isinstance(exc_value, error_type):
                extra_args = {'e': exc_value, 'error_type':error_type}
                error_string = self.error_dict[error_type]
                my_custom_error(error_string, self.args, extra_args)
                return True
        return self.thing.__exit__(exc_type, exc_value, traceback)