from ctypes import *
from ctypes import _SimpleCData
import logging.config
import os, io
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

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.window_provider:
                print(msg)
                self.window_provider.bridge.send_to_js(msg)  # Use dedicated method
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
    
    logger.handlers.clear()
    
    interceptor = InterceptorHandler(level=target_level, window_provider=window_provider)
    formatter = logging.Formatter('[%(levelname)s] (%(asctime)s) - %(message)s')
    interceptor.setFormatter(formatter)
    logger.addHandler(interceptor)
    logger.info("Logger has been initialized")
    return logger