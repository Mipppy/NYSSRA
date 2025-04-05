from ctypes import *
from ctypes import _SimpleCData
import os
from typing import Type, TypeVar, Union

T = TypeVar("T", bound=_SimpleCData)

class SRT_DLL:
    """
    Functions starting with `dll` are DLL functions.
    """
    def __init__(self):
        self.dll_init_called = False
        self.dll_path = False
        self.dll = None
        self.all_functions_loaded = False
        self.number_of_timers = 0
        self.load_dll()
        self.check_dll_loaded()
        self.define_dll_functions()
        
    
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


    def load_dll(self):
        """
        Loads the DLL from the relative 'includes/' directory.
        
        This method is called within __init__ and typically does not need to 
        be called directly.
        """
        dll_dir = os.path.abspath("includes")
        self.dll_path = os.path.join(dll_dir, "srt_data_acquisition_dll.dll")
        os.environ["PATH"] += f";{dll_dir}"

        self.dll = WinDLL(self.dll_path, winmode=0) # type: ignore

    def check_dll_loaded(self):
        """Checks if the DLL is loaded."""
        if self.dll is None:
            raise Exception("DLL not loaded. Please call load_dll() first.")

    def get_dll(self) -> WinDLL: # type: ignore
        """
        Return the DLL if it has been loaded.

        Returns:
            WinDLL: The loaded DLL instance.
        """

        self.check_dll_loaded()
        return self.dll
    
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

        self.dll.dll_set_number_of_timers.argtypes = [POINTER(c_int)]
        self.dll.dll_set_number_of_timers.restype = None

        self.dll.dll_set_comm_port.argtypes = [POINTER(c_int)]
        self.dll.dll_set_comm_port.restype = None

        self.dll.dll_assign_default_values.argtypes = None
        self.dll.dll_assign_default_values.restype = None

        self.dll.dll_start_communicating_with_timers.argtypes = None
        self.dll.dll_start_communicating_with_timers.restype = None

        self.dll.dll_stop_communicating_with_timers.argtypes = None
        self.dll.dll_stop_communicating_with_timers.restype = None

        self.dll.dll_reset_all_timer_record_counters_to_zero.argtypes = None
        self.dll.dll_reset_all_timer_record_counters_to_zero.restype = None

        self.dll.dll_exit_routine.argtypes = [c_char_p]
        self.dll.dll_exit_routine.restype = None

        self.dll.dll_initialize_dll_task.argstypes = [c_int, c_char_p]
        self.dll.dll_initialize_dll_task.restype = c_int

        self.dll.dll_generate_dummy_record.argstypes = None
        self.dll.dll_generate_dummy_record.restype = None

        self.dll.dll_reset_timers = None
        self.dll.dll_reset_timers = None

        self.dll.dll_get_next_timer_structure_from_fifo.argtypes = [POINTER(self.XC_TIMER_RECORD_STRUCTURE_TYPE)]
        self.dll.dll_get_next_timer_structure_from_fifo.restype = c_int

        self.all_functions_loaded = True

    def convert_to_ctypes(self, value: Union[int, str, bytes, T], ctype: Type[T]) -> T:
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


    @ensure_dll_loaded
    @ensure_ready_to_call_function
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
    @ensure_ready_to_call_function
    def dll_set_number_of_timers(self, timer_count: Union[int, c_int]) -> None:
        """
        Sets the number of timers.  

        Parameters:
        timer_count (int | c_int): The number of timers 
        """
        checked_timer_count = self.convert_to_ctypes(timer_count, c_int)
        self.dll.dll_set_number_of_timers(byref(checked_timer_count))
        self.number_of_timers = checked_timer_count.value
        return
    
    def get_number_of_timers(self) -> int:
        """
        Non-DLL function.  

        Returns:
        number_of_timers (int): The number of timers set.  If `dll_set_number_of_timers` has not been called, this will return 0.
        """
        return self.number_of_timers
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_comm_port(self, comm_port: Union[int, c_int]) -> None:
        """
        Set the communication port where the timers are connected.

        Parameters:
        comm_port (int | c_int): The communication port
        """
        checked_comm_port = self.convert_to_ctypes(comm_port, c_int)
        self.dll.dll_set_comm_port(byref(checked_comm_port))
        return

    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_assign_config_default_values(self) -> None:
        """
        Sets the DLL's configuration to the default values.
        This is not neccessary to call under normal circumstancs.
        """
        self.dll.dll_assign_default_values()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_start_communicating_with_timers(self) -> None:
        """
        Opens communication with timers.  
        Call after setting communication port with `dll_set_comm_port`
        """
        self.dll.dll_start_communicating_with_timers()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_stop_communicating_with_timers(self) -> None:
        """
        Stops communication with timers.
        Only call after communication is already opened.
        """
        self.dll.dll_stop_communicating_with_timers()
        return
    
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_reset_all_timer_record_counters_to_zero(self) -> None:
        """
        It is not necessary to call this function, unless you want the timers to retransmit all of their data
        """
        self.dll.dll_reset_all_timer_record_counters_to_zero()
        return
    
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_exit_routine(self, exit_string: Union[str, c_char_p]) -> None:
        """
        The following function should not be called during normal operation.\n
        It can be called if an error condition occurs.\n
        It causes the dll to quit.\n
        If you use this function, be sure to call `del CLASS_INSTANCE` afterwords to prevent memory leaks.

        Parameters:
        exit_string (str | c_char_p): The string the DLL exits with.
        """
        checked_exit_string = self.convert_to_ctypes(exit_string, c_char_p)
        self.dll.dll_exit_routine(checked_exit_string)
        self.dll = None
        self.dll_init_called = False
        return
    
    @ensure_dll_loaded
    def dll_initialize_dll_task(self, read_ini_file_flag: Union[int, c_int], race_directory: Union[str, c_char_p]) -> c_int:
        """
        <b>It is necessary to call this function.</b>\n
        The following function initializes the timer dll.
        First, this function sets members of the configuration to their default values.
        If `read_ini_file_flag` = 1, then the dll overwrites the configuration parameters with values from the .INI file.
        If `read_ini_file_flag` = 0, then the dll does not overwrites the configuration parameters with values from the .INI file.
        `race_directory` is a string with the path to directory where files are written.
        """
        checked_read_ini_file_flag = self.convert_to_ctypes(read_ini_file_flag, c_int)
        checked_race_directory = self.convert_to_ctypes(race_directory, c_char_p)
        result = self.dll.dll_initialize_dll_task(checked_read_ini_file_flag, checked_race_directory)
        self.dll_init_called = True
        return result
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_generate_dummy_record(self) -> None:
        """
        This function can be used to test the software without having any timers connected.

        More accurate description will come when I use this function.
        """
        self.dll.dll_generate_dummy_record()
        return

    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_reset_timers(self) -> None:
        """
        The following function resets all of the timers from the PC.

        More accurate description will come when I use this function.
        """
        self.dll.dll_reset_timers()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_get_next_timer_structure_from_fifo(self) -> Union[XC_TIMER_RECORD_STRUCTURE_TYPE, None]:
        """
        The following function returns a 0 when there is no data to retrieve from the dll. 
        It returns a 1 when there is    data to retrieve from the dll. 
        Data is put into the structure

        More accurate description will come when I use this function.
        """
        record = self.XC_TIMER_RECORD_STRUCTURE_TYPE()
        result = self.dll.dll_get_next_timer_structure_from_fifo(byref(record))
        if result == 1:
            return record
        return None