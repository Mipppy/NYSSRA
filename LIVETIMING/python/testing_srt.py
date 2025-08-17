# An incredibly primitive copy of SRT_TIMING/data_acquisition_module_app/timer_appDlg_090528.cpp

"""
Example timer records:
    o - Timer record: {'table_id': 0, 'device_num': 2, 'record_num': 15, 'event_num': 3, 'heat_num': 5, 'channel': 1, 'record_typ': 'b', 'userstring': '1', 'userxfield': [None, None, None, None, None, None, None, None, None, None], 'bib_string': '1', 'timer_time': '9:11:16.83', 'pc_time': '09:11:18', 'notes': ' '}
    o - Timer record: {'table_id': 0, 'device_num': 2, 'record_num': 14, 'event_num': 3, 'heat_num': 5, 'channel': 1, 'record_typ': 'b', 'userstring': '7', 'userxfield': [None, None, None, None, None, None, None, None, None, None], 'bib_string': '7', 'timer_time': '9:11:12.56', 'pc_time': '09:11:13', 'notes': ' '}
    o - Timer record: {'table_id': 0, 'device_num': 2, 'record_num': 13, 'event_num': 3, 'heat_num': 5, 'channel': 1, 'record_typ': 'b', 'userstring': '2', 'userxfield': [None, None, None, None, None, None, None, None, None, None], 'bib_string': '2', 'timer_time': '9:11:09.31', 'pc_time': '09:11:11', 'notes': ' '}
"""


from xc_timer import XC_TIMER_DLL
import time
instance = XC_TIMER_DLL()
instance.dll_initialize_dll_task(0x100 | 0x40 | 0x10 | 2,'srt/')
instance.dll_set_string_delimiter(0)

conf_data = instance.dll_get_pointer_to_configuration_structure()
global_struct = instance.dll_get_pointer_to_global_variable_structure()

instance.dll_set_comm_port(3)
instance.dll_start_communicating_with_timers()
instance.dll_set_event_and_heat(0, 3, 5)
instance.dll_synch_timers(0, "0")


while True:
    while True:
        d = instance.dll_get_character_from_terminal_fifo()
        if d == -1:
            break
        print("Terminal char:", chr(d) if d < 128 else d)

    while True:
        record = instance.dll_get_next_timer_structure()
        if not record:
            break
        print("Timer record:", record.as_dict())

    # !!!! ~50 MS CLOCK !!!!
    time.sleep(0.05)  

