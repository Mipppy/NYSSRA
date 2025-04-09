from ctypes import *
from ctypes import _SimpleCData
import os
from typing import Type, TypeVar, Union
from helpers import convert_to_ctypes, ensure_dll_loaded, ensure_ready_to_call_function, XC_TIMER_RECORD_STRUCTURE_TYPE


class SRT_ACQUISITION_DLL:
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

        self.dll.dll_reset_timers.argstypes = None
        self.dll.dll_reset_timers.restype = None

        self.dll.dll_synch_timers.argstypes = [c_int, c_char_p]
        self.dll.dll_synch_timers.restype = None

        self.dll.dll_put_timer_structure_into_fifo.argtypes = [POINTER(self.XC_TIMER_RECORD_STRUCTURE_TYPE)]
        self.dll.dll_put_timer_structure_into_fifo.restype = c_int

        self.dll.dll_disable_timer_reset.argstypes = None
        self.dll.dll_disable_timer_reset.restype = None

        self.dll.dll_reset_all_timer_record_counters_to_zero.argstypes = None
        self.dll.dll_reset_all_timer_record_counters_to_zero.restype = None

        self.dll.dll_set_string_delimiter.argstypes = [POINTER(c_int)]
        self.dll.dll_set_string_delimiter.restype = None

        self.dll.dll_delete_dll_fifo_records.argstypes = None
        self.dll.dll_delete_dll_fifo_records.restype = None

        self.dll.dll_set_diagnostic_flags.argstypes = [POINTER(c_int)]
        self.dll.dll_set_diagnostic_flags.restype = None

        self.all_functions_loaded = True

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
        checked_value1 = convert_to_ctypes(value1, c_long)
        checked_value2 = convert_to_ctypes(value2, c_long)
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
        checked_timer_count = convert_to_ctypes(timer_count, c_int)
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
        checked_comm_port = convert_to_ctypes(comm_port, c_int)
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
        checked_exit_string = convert_to_ctypes(exit_string, c_char_p)
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
        checked_read_ini_file_flag = convert_to_ctypes(read_ini_file_flag, c_int)
        checked_race_directory = convert_to_ctypes(race_directory, c_char_p)
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
    def dll_put_timer_structure_into_fifo(self) -> Union[XC_TIMER_RECORD_STRUCTURE_TYPE, None]:
        """
        The following function returns None when there is no data to retrieve from the dll. 
        It returns a XC_TIMER_RECORD_STRUCTURE_TYPE when there is data to retrieve from the dll. 
        Data is put into the structure

        More accurate description will come when I use this function.
        """
        record = self.XC_TIMER_RECORD_STRUCTURE_TYPE()
        result = self.dll.dll_put_timer_structure_into_fifo(byref(record))
        if result == 1:
            return record
        return None
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_synch_timers(self,synch_timers_flag: Union[int, c_int], synch_time_string: Union[str, c_char_p]) -> None:
        """
        The following function synchs all of the timers.
        <hr>
        Set synch_timers_flag = 0 for synching to the PC clock.\n
        Set synch_timers_flag = 1 for synching to a wristwatch.  The synch_time_string contains the time to synch to.\n
        Set synch_timers_flag = 2 for adjusting the synch time by a certain amount. The synch_time_string contains the amount of adjustment
        """
        checked_synch_timers_flag = convert_to_ctypes(synch_timers_flag, c_int)
        checked_synch_time_string = convert_to_ctypes(synch_time_string, c_char_p)
        self.dll.dll_synch_timers(checked_synch_timers_flag, checked_synch_time_string)
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_disable_timer_reset(self) -> None:
        """
        The following function disables the ability to reset the timers from the PC.
        """
        self.dll.dll_disable_timer_reset()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_reset_all_timer_record_counters_to_zero(self) -> None:
        """
        It is not necessary to call this function, unless you want the timers to retransmit all of their data
        
        More accurate description will come when I use this function. 
        """ 
        self.dll.dll_reset_all_timer_record_counters_to_zero()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_string_delimiter(self, new_string_delimiter: Union[int, c_int]) -> None:
        """
        Just never use this function, I'm only including it for the sake of including every function the DLL.
        
        This terminates returned strings with the set value.  The default is 0 and in the past it was !.
        """
        checked_new_string_delmiter = convert_to_ctypes(new_string_delimiter, c_int)
        self.dll.dll_set_string_delimiter(byref(checked_new_string_delmiter))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_delete_dll_fifo_records(self) -> None:
        """
        More accurate description will come when I use this function. 
        """
        self.dll.dll_delete_dll_fifo_records()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_diagnostic_flags(self, new_flag: Union[int,c_int]) -> None:
        """
        More accurate description will come when I use this function. 

        Args:
            new_flag (Union[int,c_int]): I <b>presume</b> that the this is either 0 or 1, so don't set any other value.
        """
        checked_new_flag = convert_to_ctypes(new_flag)
        self.dll.dll_set_diagnostic_flags(byref(checked_new_flag))
        return