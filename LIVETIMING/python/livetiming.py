from srt_acquisition import SRT_ACQUISITION_DLL
from xc_timer import XC_TIMER_DLL
from ctypes import *
from helpers import get_storage_location

xc_instance = XC_TIMER_DLL()
xc_instance.dll_initialize_dll_task(0x110, get_storage_location())
xc_instance.dll_set_comm_port(2)
xc_instance.dll_set_diagnostic_flags(1)
xc_instance.dll_set_string_delimiter(0)
xc_instance.dll_generate_dummy_record()
record = xc_instance.dll_get_next_timer_record()
for key,item in record.items():
    print(f"Key: {key}  - Value: {item}")