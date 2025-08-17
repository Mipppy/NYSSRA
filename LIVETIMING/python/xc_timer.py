from __future__ import annotations
from ctypes import *
from ctypes import _SimpleCData
import os
from typing import Type, TypeVar, Union, TYPE_CHECKING, TypeAlias, Protocol
from helpers import *
import logging
from datetime import datetime

class XC_TIMER_DLL:
    def __init__(self):
        self.dll_init_called = False
        self.dll = None
        self.timer_number = 0
        self.logger = logging.getLogger('BART2')
        self.all_functions_loaded = False
        self.load_dll()
        self.register_dll_functions()
        self.logger.info("Successfully loaded xc_timer_dll.dll")
        
    def load_dll(self) -> None:
        """
        Loads the DLL from the relative 'includes/' directory.
        
        This method is called within __init__ and typically does not need to 
        be called directly.
        """
        dll_dir = os.path.abspath("includes")
        self.dll_path = os.path.join(dll_dir, "xc_timer_dll.dll")
        os.environ["PATH"] += f";{dll_dir}"
        print(self.dll_path)
        self.dll = WinDLL(self.dll_path) # type: ignore
    
    # Recreating the structures used within the DLL so we can send a pointer over for some function arguments.
    class XC_TIMER_RECORD_STRUCTURE_TYPE(AutoDecodingStructure):
        table_id:int;device_num:int;record_num:int;event_num:int;heat_num:int;channel:int;record_typ:str;userstring:str;userxfield:List[str];bib_string:str;timer_time:str|datetime;pc_time:str|datetime;notes:str
        _fields_ = [
            ("table_id", c_uint),
            ("device_num", c_ushort),
            ("record_num", c_uint),
            ("event_num", c_ushort),
            ("heat_num", c_ushort),
            ("channel", c_ushort),
            ("record_typ", c_char * 20),
            ("userstring", c_char * 20),
            ("userxfield", (c_char * 20) * 10),
            ("bib_string", c_char * 20),
            ("timer_time", c_char * 20),
            ("pc_time", c_char * 20),
            ("notes", c_char * 50),
        ]

    class XC_CONFIGURE_STRUCTURE_TYPE(AutoDecodingStructure):
        _fields_ = [
            ("serial_comm_port", c_uint),  
            ("baud_rate", c_ulong),
            ("number_of_devices_used", c_ushort),
            ("talk_time", c_ushort),
            ("string_delimiter", c_char),
            ("left_justify_time_strings_flag", c_ubyte),
            ("password", c_long),
            ("diagnostic_flags", c_uint),
            ("database_highest_record_number", c_ulong),
            ("highest_record_received_array", c_ushort * 32),
            ("timer_type_used", c_char * 100),
            ("database_type", c_char * 100),
            ("database_drive", c_char * 100),
            ("database_directory", c_char * 400),
            ("database_name", c_char * 400),
            ("database_extension", c_char * 400),
            ("database_table_name", c_char * 400),
            ("odbc_user_dsn_flag", c_ubyte),
            ("database_odbc_user_data_source_name", c_char * 400),
            ("event_number", c_uint),
            ("heat_number", c_uint),
        ]
    class GLOBAL_VARIABLE_STRUCTURE_TYPE(AutoDecodingStructure):
        _fields_ = [
            ("version_number_string", c_char * 200),
            ("version_time_string", c_char * 200),
            ("version_date_string", c_char * 200),

            ("race_directory", c_char * 500),
            ("database_path_and_file_name", c_char * 500),
            ("current_working_directory", c_char * 500),
            ("log_file_path_and_name", c_char * 500),
            ("tx_file_path_and_name", c_char * 500),
            ("rx_file_path_and_name", c_char * 100),
            ("ini_file_path_and_name", c_char * 100),
            ("backup_file_path_and_name", c_char * 100),

            ("srt_1000_used_flag", c_ubyte),
            ("tag_heuer_505_used_flag", c_ubyte),
            ("tag_heuer_605_used_flag", c_ubyte),
            ("hora_targets_used_flag", c_ubyte),

            ("timer_event_interval", c_int),
            ("timer_event_resolution", c_int),
        ]
        
    @ensure_dll_loaded
    def register_dll_functions(self) -> None:
        """
        Register the DLL's functions.

        This method is called within __init__ and typically does not need to 
        be called directly.
        """
        self.dll.dll_initialize_dll_task.argstypes = [POINTER(c_long), c_char_p]
        self.dll.dll_initialize_dll_task.restype = c_long
        
        self.dll.dll_exit_routine.argstypes = [c_char_p]
        self.dll.dll_exit_routine.restype = c_long
        
        self.dll.dll_generate_dummy_record.argstypes = None
        self.dll.dll_generate_dummy_record.restype = c_long
        
        self.dll.dll_synch_timers.argstypes = [POINTER(c_long), c_char_p]
        self.dll.dll_synch_timers.restype = c_long
        
        self.dll.dll_get_character_from_terminal_fifo.argstypes = None
        self.dll.dll_get_character_from_terminal_fifo.restype = c_long
        
        self.dll.dll_delete_records_in_backup_text_file.argstypes = None
        self.dll.dll_delete_records_in_backup_text_file.restype = c_long
        
        self.dll.dll_reset_all_timer_record_counters_to_zero.argstypes = None
        self.dll.dll_reset_all_timer_record_counters_to_zero.restype = c_long
        
        self.dll.dll_set_number_of_timers.argstypes = [POINTER(c_long)]
        self.dll.dll_set_number_of_timers.restype = c_long
        
        self.dll.dll_set_comm_port.argstypes = [POINTER(c_long)]
        self.dll.dll_set_comm_port.restype = c_long
        
        self.dll.dll_set_talk_time.argstypes = [POINTER(c_long)]
        self.dll.dll_set_talk_time.restype = c_long
        
        self.dll.dll_set_string_delimiter.argstypes = [POINTER(c_long)]
        self.dll.dll_set_string_delimiter.restype = c_long
        
        self.dll.dll_set_diagnostic_flags.argstypes = [POINTER(c_long)]
        self.dll.dll_set_diagnostic_flags.restype = c_long
        
        self.dll.dll_test_function_call_passing_string.argstypes = [c_char_p, c_char_p]
        self.dll.dll_test_function_call_passing_string.restype = c_long
        
        self.dll.dll_get_msec_since_last_communication.argstypes = [POINTER(c_long)]
        self.dll.dll_get_msec_since_last_communication.restype = c_long
        
        self.dll.dll_start_communicating_with_timers.argstypes = None
        self.dll.dll_start_communicating_with_timers.restype = c_long
        
        self.dll.dll_stop_communicating_with_timers.argstypes = None
        self.dll.dll_stop_communicating_with_timers.restype = c_long
        
        # Within the DLL, this is actually just a wrapper for dll_get_next_timer_record, but it clearly a later version, as it uses the XC_TIMER_RECORD_STRUCTURE_TYPE, rather than doing each field of it individually.
        # dll_get_next_timer_record is not needed (and really should never be used), so I'm not bothering implementing it here.
        self.dll.dll_get_next_timer_structure.argstypes = [POINTER(c_long), POINTER(self.XC_TIMER_RECORD_STRUCTURE_TYPE)]
        self.dll.dll_get_next_timer_structure.restype = c_long
        
        self.dll.dll_get_pointer_to_configuration_structure.argstypes = None
        self.dll.dll_get_pointer_to_configuration_structure.restype = POINTER(self.XC_CONFIGURE_STRUCTURE_TYPE)
        
        self.dll.dll_get_pointer_to_global_variable_structure.argstypes = None
        self.dll.dll_get_pointer_to_global_variable_structure.restype = POINTER(self.GLOBAL_VARIABLE_STRUCTURE_TYPE)
        
        self.dll.dll_set_baud_rate.argstypes = [POINTER(c_long)]
        self.dll.dll_set_baud_rate.restype = c_long
        
        self.dll.dll_assign_default_values.argstypes = None
        self.dll.dll_assign_default_values.restype = c_long
        
        self.dll.dll_set_event_and_heat.argstypes = [POINTER(c_long), POINTER(c_long), POINTER(c_long)]
        self.dll.dll_set_event_and_heat.restype = c_long
        
        self.dll.dll_disable_timer_reset.argstypes = None
        self.dll.dll_disable_timer_reset.restype = c_long
        
        self.logger.debug("Loaded xc_timer_dll.dll's functions successfully.")
        
        self.all_functions_loaded = True
        
        
    @ensure_dll_loaded
    def dll_initialize_dll_task(self, initialize_method:Union[int, c_long],race_directory:Union[str, c_char_p]) -> int:
        """
        <b>It is necessary to call this function.</b>\n
        <b>VERY IMPORTANT!!!! SET `initialize_method` to 0x110 TO ENABLE LOGGING!!!</b>\n
        The following function initializes the timer dll.
        First, this function sets members of the configuration to their default values.\n
        If `read_ini_file_flag` = 1, then the dll overwrites the configuration parameters with values from the .INI file.\n
        If `read_ini_file_flag` = 0, then the dll does not overwrites the configuration parameters with values from the .INI file.
        Args:
            initialize_method (Union[int, c_long]): Read above
            race_directory (Union[str, c_char_p]): a string with the path to directory where files are written.
        """
        # Returns 1 no matter what.
        c_initialize_method = convert_to_ctypes(initialize_method, c_long)
        c_race_directory = convert_to_ctypes(race_directory, c_char_p)
        returned_value = self.dll.dll_initialize_dll_task(byref(c_initialize_method), c_race_directory)
        self.dll_init_called = True
        return returned_value
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_exit_routine(self, exit_string: Union[str, c_char_p]) -> None:
        """
        Exits the DLL.  This should <b>never</b> be called under normal circumstances.  
        Only call this when critical errors occur and the program is not savagable.

        Args:
            exit_string (Union[str, c_char_p]): The string that the DLL exits with.
        """
        c_exit_string = convert_to_ctypes(exit_string, c_char_p)
        self.dll.dll_exit_routine(c_exit_string)
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_generate_dummy_record(self) -> None:
        """
        Puts a Dummy XC_TIMER_RECORD_STRUCTURE_TYPE in the FIFO.
        Uses "" and 9999 for the dummy values
        """
        self.dll.dll_generate_dummy_record()
        return 
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_synch_timers(self, synch_timers_flag: Union[int, c_long], synch_timers_string: Union[str, c_char_p]) -> None:
        """
        The following function synchs all of the timers.
        <hr>
        Set synch_timers_flag = 0 for synching to the PC clock.\n
        Set synch_timers_flag = 1 for synching to a wristwatch.  The synch_time_string contains the time to synch to.\n
        Set synch_timers_flag = 2 for adjusting the synch time by a certain amount. The synch_time_string contains the amount of adjustment
        """
        c_synch_timers_flag = convert_to_ctypes(synch_timers_flag, c_long)
        c_synch_timers_string = convert_to_ctypes(synch_timers_string, c_char_p)
        self.dll.dll_synch_timers(byref(c_synch_timers_flag), c_synch_timers_string)
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_get_character_from_terminal_fifo(self) -> c_long:
        """
        Reads from the terminal FIFO
        
        From using this function, I believe it logs the raw data sent by the timers to the modem, such as pings.
        More information will be added as this function is used.
        """
        return self.dll.dll_get_character_from_terminal_fifo()
        
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_delete_records_in_backup_text_file(self) -> None:
        """
        Deletes records in backup text file.  This function does have a return value, but it will always be 1
        
        More information will be added as this function is used.
        """
        self.dll.dll_delete_records_in_backup_text_file()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_reset_all_timer_record_counters_to_zero(self) -> None:
        """
        It is not necessary to call this function, unless you want the timers to retransmit all of their data
        
        More information will be added as this function is used.
        """
        self.dll.dll_reset_all_timer_record_counters_to_zero()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_number_of_timers(self, number_of_timers:Union[int,c_long]) -> None:
        """
        Does the obvious
        """
        self.timer_number = int(number_of_timers)
        c_number_of_timers = convert_to_ctypes(number_of_timers, c_long)
        self.dll.dll_set_number_of_timers(byref(c_number_of_timers))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_comm_port(self, comm_port:Union[int,c_long]) -> None:
        """
        The following function does the obvious thing (1 for COMM1, 2 for COMM2, etc).  Default is COMM 1


        Args:
            comm_port (Union[int,c_long]): The new comm port.
        """
        c_comm_port = convert_to_ctypes(comm_port, c_long)
        self.dll.dll_set_comm_port(byref(c_comm_port))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_talk_time(self, talk_rate: Union[int, c_long]) -> None:
        """
         The following function sets talk time (msec). Talk time is the time duration, where a particular device has the token and can talk on the RS485 line.  Default is 400 msec.

        Args:
            talk_rate (Union[int, c_long]): The new talk rate.
        """
        c_talk_rate = convert_to_ctypes(talk_rate, c_long)
        self.dll.dll_set_talk_time(byref(c_talk_rate))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_string_delimiter(self, string_delimiter: Union[int, c_long]) -> None:
        """
        Default is terminating strings with '!!'

        Args:
            string_delimiter (Union[int, c_long]): The new string delimiter
        """
        c_string_delimiter = convert_to_ctypes(string_delimiter, c_long)
        self.dll.dll_set_string_delimiter(byref(c_string_delimiter))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_diagnostic_flags(self, flag_state:Union[int,c_long]) -> None:
        """
        More information will come when I use this

        Args:
            flag_state (Union[int,c_long]): New state.  0 is off and 1 is on
        """
        c_flag_state = convert_to_ctypes(flag_state, c_long)
        self.dll.dll_set_diagnostic_flags(byref(c_flag_state))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_test_function_call_passing_string(self, string1:Union[str,c_char_p], string2:Union[str,c_char_p]) -> c_long:
        """
        A test function to test if the DLL is successfully loaded or not.

        Args:
            string1 (Union[str,c_char_p]): Will be set to "Hello world from Timer DLL!"
            string2 (Union[str,c_char_p]): Have Fun!

        Returns:
            c_long: Will be 314159
        """
        c_string1 = convert_to_ctypes(string1, c_char_p)
        c_string2 = convert_to_ctypes(string2, c_char_p)
        return self.dll.dll_test_function_call_passing_string(c_string1, c_string2)
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_get_msec_since_last_communication(self, device_num:Union[int,c_long]) -> c_long:
        """
        Gets the msec since the device has last sent a packet.  Returns 0 on failure

        Args:
            device_num (Union[int,c_long]): The number of the device.  

        Returns:
            c_long: The msec since last packet
        """
        if int(device_num) > self.timer_number - 1:
            return c_long(0)
        c_device_num = convert_to_ctypes(device_num, c_long)
        return self.dll.dll_get_msec_since_last_communication(byref(c_device_num))
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_start_communicating_with_timers(self) -> None:
        """
        Why don't you figure this one out pal
        """
        self.dll.dll_start_communicating_with_timers()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_stop_communicating_with_timers(self) -> None:
        """
        You figured out how to start it, why not stop it?
        """
        self.dll.dll_stop_communicating_with_timers()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_get_pointer_to_global_variable_structure(self) -> GLOBAL_VARIABLE_STRUCTURE_TYPE:
        ptr = self.dll.dll_get_pointer_to_global_variable_structure()
        struct_ptr = cast(ptr, POINTER(self.GLOBAL_VARIABLE_STRUCTURE_TYPE))
        return struct_ptr.contents
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_get_pointer_to_configuration_structure(self) -> XC_CONFIGURE_STRUCTURE_TYPE:
        ptr = self.dll.dll_get_pointer_to_configuration_structure()
        struct_ptr = cast(ptr, POINTER(self.XC_CONFIGURE_STRUCTURE_TYPE))
        return struct_ptr.contents 


    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_get_next_timer_structure(self) -> Union[XC_TIMER_RECORD_STRUCTURE_TYPE, None]:
        app = c_long(0)
        rec = self.XC_TIMER_RECORD_STRUCTURE_TYPE()
        res = self.dll.dll_get_next_timer_structure(byref(app), byref(rec))

        if res != 1:
            return None
        return rec 
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_get_pointer_to_configuration_structure(self) -> dict:
        """
        Gets the pointer to the XC_CONFIGURE_STRUCTURE_TYPE within the DLL.

        Returns:
            XC_CONFIGURE_STRUCTURE_TYPE: The structure type within the DLL. 
        """
        ptr = self.dll.dll_get_pointer_to_configuration_structure()
        struct_ptr = cast(ptr, POINTER(self.XC_CONFIGURE_STRUCTURE_TYPE))
        return struct_ptr.contents.as_dict()
        
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_baud_rate(self, baud_rate:Union[int,c_long]) -> None:
        """
        <b>Never call this function.  The only working baud rate is the default 9600.</b>
        <hr>
        The following function does the obvious thing.  Default is 9600.  That is the only baud rate currently supported


        Args:
            baud_rate (Union[int,c_long]): The new baud rate
        """
        c_baud_rate = convert_to_ctypes(baud_rate, c_long)
        self.dll.dll_set_baud_rate(byref(c_baud_rate))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_assign_default_values(self) -> None:
        """
        The following function sets variables back to their default values
        It is not necessary to call this function
        """ 
        self.dll.dll_assign_default_values()
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_set_event_and_heat(self, device:Union[int, c_long], event:Union[int, c_long], heat:Union[int, c_long]) -> None:
        """
        The following function sends event and heat information to the timers.
        If device = 0, then the event and heat information is sent to all timers

        Args:
            device (Union[int, c_long]): The device number, typically set this to 0
            event (Union[int, c_long]): The current event
            heat (Union[int, c_long]): The current heat
        """
        c_device = convert_to_ctypes(device, c_long)
        c_event = convert_to_ctypes(event, c_long)
        c_heat = convert_to_ctypes(heat, c_long)
        self.dll.dll_set_event_and_heat(byref(c_device), byref(c_event), byref(c_heat))
        return
    
    @ensure_dll_loaded
    @ensure_ready_to_call_function
    def dll_disable_timer_reset(self) -> None:
        """
        The following function disables the ability to reset the timers from the PC

        Note: From what I can tell, this function must serve some other purpose, as it used in the 2 code examples provided.\n
        I would call this just to be careful.
        """
        self.dll.dll_disable_timer_reset()
        return
    
    def dll_get_initialization_flag(self) -> bool:
        """
        This function exists within the DLL, but it is easier for us to track, and it saves a call to the DLL.

        Returns:
            bool: Whether or not the DLL has been initialized.
        """
        return self.dll_init_called


# # Expose for typing.
# if TYPE_CHECKING:
#     class XC_TIMER_RECORD_STRUCTURE_PROTOCOL(Protocol):
#         table_id: int
#         device_num: int
#         record_num: int
#         event_num: int
#         heat_num: int
#         channel: int
#         record_typ: str
#         userstring: str
#         userxfield: list[str]  
#         bib_string: str
#         timer_time: str
#         pc_time: str
#         notes: str
#     class XC_CONFIGURE_STRUCTURE_PROTOCOL(Protocol):
#         serial_comm_port: int
#         baud_rate: int
#         number_of_devices_used: int
#         talk_time: int
#         string_delimiter: str
#         left_justify_time_strings_flag: int
#         password: int
#         diagnostic_flags: int
#         database_highest_record_number: int
#         highest_record_received_array: list[int] 
#         timer_type_used: str
#         database_type: str
#         database_drive: str
#         database_directory: str
#         database_name: str
#         database_extension: str
#         database_table_name: str
#         odbc_user_dsn_flag: int
#         database_odbc_user_data_source_name: str
#         event_number: int
#         heat_number: int


#     class GLOBAL_VARIABLE_STRUCTURE_PROTOCOL(Protocol):
#         version_number_string: str
#         version_time_string: str
#         version_date_string: str
#         race_directory: str
#         database_path_and_file_name: str
#         current_working_directory: str
#         log_file_path_and_name: str
#         tx_file_path_and_name: str
#         rx_file_path_and_name: str
#         ini_file_path_and_name: str
#         backup_file_path_and_name: str
#         srt_1000_used_flag: int
#         tag_heuer_505_used_flag: int
#         tag_heuer_605_used_flag: int
#         hora_targets_used_flag: int
#         timer_event_interval: int
#         timer_event_resolution: int
#     XC_TIMER_RECORD_STRUCTURE_TYPE = XC_TIMER_RECORD_STRUCTURE_PROTOCOL
#     XC_CONFIGURE_STRUCTURE_TYPE = XC_CONFIGURE_STRUCTURE_PROTOCOL
#     GLOBAL_VARIABLE_STRUCTURE_TYPE = GLOBAL_VARIABLE_STRUCTURE_PROTOCOL