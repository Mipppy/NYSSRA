from ctypes import *
from ctypes import _SimpleCData
import logging.config
import os
import io
import sys
import subprocess
import logging
from pathlib import Path
from typing import Type, TypeVar, Union, Optional, List

T = TypeVar("T", bound=_SimpleCData)

def convert_to_ctypes(value: Union[int, str, bytes, T], ctype: Type[T]) -> T:
    """
    Converts a native Python value to a ctypes value of the specified type.
        
    Handles special cases like c_char_p (expects bytes or str).
    """
    if isinstance(value, ctype):
        return value  
        
    if ctype == c_char_p:
        if isinstance(value, str):
            return create_string_buffer(value.encode("utf-8"))  
        elif isinstance(value, bytes):
            return create_string_buffer(value)
        else:
            raise TypeError(f"Cannot convert {type(value)} to c_char_p")

    return ctype(value)

def ensure_ready_to_call_function(func):
    """
    A decorator to ensure that functions are ready to be called before they are.
    Throws error if conditions are not met.
    """
    def wrapper(self, *args, **kwargs):
        if not self.all_functions_loaded or not self.dll_init_called:
            raise RuntimeError('"dll_initialize_dll_task" has not been called yet.')
        return func(self, *args, **kwargs)
    return wrapper

def ensure_dll_loaded(func):
    """
    A decorator to ensure that self.dll is loaded before running the function.
    """
    def wrapper(self, *args, **kwargs):
        if not self.dll:
            raise RuntimeError("DLL has not been loaded yet.")
        return func(self, *args, **kwargs)
    return wrapper
    
class XC_TIMER_RECORD_STRUCTURE_TYPE(Structure):
    """
    A structure made very early into development that doesn't work, but is still important as it shows me what the structure looks like.

    Args:
        Structure (_type_): _description_
    """
    _fields_ = [
        ('app', c_long),
        ('table_id', c_long),
        ('device_num', c_long),
        ('record_num', c_long),
        ('event_num', c_long),
        ('heat_num', c_long),
        ('channel', c_long),
        ('record_typ', c_char),
        ('userstring', c_char * 100),
        ('user1_string', c_char * 100),
        ('user2_string', c_char * 100),
        ('user3_string', c_char * 100),
        ('user4_string', c_char * 100),
        ('bib_string', c_char * 100),
        ('timer_time', c_char * 100),
        ('pc_time', c_char * 100),
        ('notes', c_char * 100)
    ]

class InterceptorHandler(logging.Handler):
    """
    A custom logging handler that intercepts log messages in memory.
    """
    def __init__(self, level=logging.NOTSET, window_provider=None):
        super().__init__(level)
        self._log_stream = io.StringIO()
        self.window_provider = window_provider
        self.all_messages_before_js_init = []
        self.is_js_init = False


    def emit(self, record):
        try:
            msg = self.format(record)
            if "JavaScript connection initialized" in msg and self.is_js_init == False:
                self.is_js_init = True
            if self.window_provider and self.is_js_init == True:
                if self.all_messages_before_js_init != []:
                    for saved_msg in self.all_messages_before_js_init:
                        self.window_provider.bridge.send_to_js("LOG|||" + saved_msg)
                    self.all_messages_before_js_init = []
                    
                self.window_provider.bridge.send_to_js("LOG|||" + msg)
            else:
                self.all_messages_before_js_init.append(msg)  
            print(msg)
            self._log_stream.write(msg + '\n')
        except Exception:
            self.handleError(record)

    def get_logs(self) -> str:
        """
        Retrieve the intercepted logs as a single string.
        """
        return self._log_stream.getvalue()

    def clear(self):
        """
        Clear the captured log messages.
        """
        self._log_stream = io.StringIO()

def initialize_logger(verbose: bool = False, 
                    log_file: Optional[str] = None,
                    window_provider=None) -> logging.Logger:
    """
    Initialize logger with both console and file output.
    
    Args:
        verbose: If True, sets DEBUG level; otherwise INFO level
        log_file: Optional path to log file (default: 'bart2.log')
        window_provider: Optional function that returns the window instance
    
    Returns:
        Configured logger instance
    """
    
    reset_loggers()
    
    if log_file is None:
        log_file = 'bart2.log'
    
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logging.config.fileConfig(
        'bart2_logging.conf',
        defaults={'logfilename': log_file},
        disable_existing_loggers=False
    )
    
    logger = logging.getLogger('BART2')
    target_level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(target_level)
    print('\n\n\n\n\n\nLOGGER CALLED\n\n\n\n\n')
    
    interceptor = InterceptorHandler(level=target_level, window_provider=window_provider)
    formatter = logging.Formatter(f'[%(levelname)s] (%(asctime)s) {"[%(filename)s:%(lineno)d]" if verbose else ""} - %(message)s')
    interceptor.setFormatter(formatter)
    logger.addHandler(interceptor)
    logger.info("Successfully loaded Logger.")
    return logger


def reset_loggers():
    """
    This attempts to solve the issue with there being 2 BART2 loggers present, due to a bug that has no actual effect on the program, so I don't care to fix it.
    This doesn't work.
    """
    root_logger = logging.getLogger()

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    
    for logger_name in list(logging.root.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True  

        if not isinstance(logger, logging.Logger):
            continue

def openFileInExplorer(relative_path: str):
        """
        This is used for the HTML/JS when it needs to open a file in file explorer.
        This is for user convinence.

        Args:
            relative_path (str): The relative path to the file you want to open in file explorer
        """
        abs_path = Path(relative_path).resolve()

        if abs_path.exists():
            if abs_path.is_file():
                folder = abs_path.parent
            else:
                folder = abs_path

            try:
                if sys.platform == "win32":
                    os.startfile(str(folder))
                elif sys.platform == "darwin":
                    subprocess.call(["open", str(folder)])
                else:  
                    subprocess.call(["xdg-open", str(folder)])
            except Exception as e:
                print(f"Error opening path: {e}")
        else:
            print(f"Path does not exist: {abs_path}")
