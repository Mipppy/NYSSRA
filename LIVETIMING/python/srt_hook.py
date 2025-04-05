from ctypes import *
import os
from typing import Type, TypeVar, Union

T = TypeVar("T", bound=c_long)

class SRT_DLL:
    def __init__(self):
        self.load_dll()
        self.check_dll_loaded()
        self.define_dll_functions()
    
    def ensure_functions_loaded(func):
        """
        A decorator to ensure that self.all_functions_loaded is True before running the function.
        """
        def wrapper(self, *args, **kwargs):
            if not self.all_functions_loaded:
                raise RuntimeError("Functions have not been loaded yet.")
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


    def load_dll(self):
        """
        Loads the DLL from the relative 'includes/' directory.
        
        This method is called within __init__ and typically does not need to 
        be called directly.
        """
        dll_dir = os.path.abspath("includes")
        self.dll_path = os.path.join(dll_dir, "srt_data_acquisition_dll.dll")
        os.environ["PATH"] += f";{dll_dir}"

        self.dll = WinDLL(self.dll_path, winmode=0)

    def check_dll_loaded(self):
        """Checks if the DLL is loaded."""
        if self.dll is None:
            raise Exception("DLL not loaded. Please call load_dll() first.")

    def get_dll(self) -> WinDLL:
        """
        Return the DLL if it has been loaded.

        Returns:
            WinDLL: The loaded DLL instance.
        """

        self.check_dll_loaded()
        return self.dll
    
    @ensure_dll_loaded
    def define_dll_functions(self):
        """
        Register the DLL's functions.

        This method is called within __init__ and typically does not need to 
        be called directly.
        """
        self.dll.dll_test_function_call_passing_long.argtypes = [POINTER(c_long), POINTER(c_long)]
        self.dll.dll_test_function_call_passing_long.restype = c_long  

        self.dll.dll_initialize_dll_task.argtypes = [c_int, c_char_p]
        self.dll.dll_initialize_dll_task.restype = c_int

        self.dll.dll_set_number_of_timers.argtypes = [c_int]
        self.dll.dll_set_number_of_timers.restype = None

        self.dll.dll_set_comm_port.argtypes = [c_int]
        self.dll.dll_set_comm_port.restype = None

        self.dll.dll_assign_default_values.argtypes = None
        self.dll.dll_assign_default_values.restype = None

        self.dll.dll_start_communicating_with_timers.argtypes = None
        self.dll.dll_start_communicating_with_timers.restype = None

        self.dll.dll_stop_communicating_with_timers.argtypes = None
        self.dll.dll_stop_communicating_with_timers.restype = None

        self.dll.dll_empty_backup_text_file.argtypes = None
        self.dll.dll_empty_backup_text_file.restype = None

        self.dll.dll_reset_all_timer_record_counters_to_zero.argtypes = None
        self.dll.dll_reset_all_timer_record_counters_to_zero.restype = None

        self.all_functions_loaded = True

    def convert_to_ctypes(self, value: Union[int, T], ctype: Type[T]) -> T:
        """
        Converts an integer to the specified ctypes type if needed.

        Parameters:
        value (int | T): The number to process.
        ctype (Type[T]): The ctypes type to convert to.

        Returns:
        T: The value as the specified ctypes type.
        """
        if isinstance(value, int):
            return ctype(value)  
        return value  

    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_test_long(self, value1: Union[int, c_long], value2: Union[int, c_long]) -> c_long:
        """
        Runs the DLL long test function. Simply adds the 2 numbers. 

        Parameters:
        value1 (int | c_long): First number
        value2 (int | c_long): Second number

        Returns:
        result (c_long): The sum of the 2 numbers
        """
        checked_value1 = self.convert_to_ctypes(value1, c_long)
        checked_value2 = self.convert_to_ctypes(value2, c_long)
        result = self.dll.dll_test_function_call_passing_long(byref(checked_value1), byref(checked_value2))
        return result

    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_set_number_of_timers(self, timer_count: Union[int, c_int]) -> None:
        """
        Sets the number of timers.  

        Parameters:
        timer_count (int | c_int): The number of timers 
        """
        self.dll.dll_set_number_of_timers(self.convert_to_ctypes(timer_count, c_int))
        return
    
    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_set_comm_port(self, comm_port: Union[int, c_int]) -> None:
        """
        Set the communication port where the timers are connected.

        Parameters:
        comm_port (int | c_int): The communication port
        """
        self.dll.dll_set_comm_port(self.convert_to_ctypes(comm_port, c_int))
        return

    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_assign_config_default_values(self) -> None:
        """
        Sets the DLL's configuration to the default values.
        This is not neccessary to call under normal circumstancs.
        """
        self.dll.dll_assign_default_values()
        return
    
    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_start_communicating_with_timers(self) -> None:
        """
        Opens communication with timers.  
        Call after setting communication port with `dll_set_comm_port`
        """
        self.dll.dll_start_communicating_with_timers()
        return
    
    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_stop_communicating_with_timers(self) -> None:
        """
        Stops communication with timers.
        Only call after communication is already opened.
        """
        self.dll.dll_stop_communicating_with_timers()
        return
    
    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_empty_backup_text_file(self) -> None:
        """
        Clears the backup text file for the DLL.
        """
        self.dll.dll_empty_backup_text_file()
        return
    
    @ensure_dll_loaded
    @ensure_functions_loaded
    def dll_reset_all_timer_record_counters_to_zero(self) -> None:
        """
        It is not necessary to call this function, unless you want the timers to retransmit all of their data
        """
        self.dll.dll_reset_all_timer_record_counters_to_zero()
        return
    
    