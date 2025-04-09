from ctypes import *
from ctypes import _SimpleCData
import os
from typing import Type, TypeVar, Union


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
        A decorator to ensure that functions are ready to be called before they are.  Throws error if conditions are not met.
        """
        def wrapper(self, *args, **kwargs):
            if not self.all_functions_loaded or not self.dll_init_called:
                raise RuntimeError('"dll_initialize_dll_task" has not been called yet. ')
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