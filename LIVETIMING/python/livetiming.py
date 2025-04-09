from srt_acquisition import SRT_ACQUISITION_DLL
from xc_timer import XC_TIMER_DLL
from ctypes import *

xc_instance = XC_TIMER_DLL()
xc_instance.dll_initialize_dll_task(1, "Z:/home/tim/Documents/Programs/NYSSRA/LIVETIMING/python/")
xc_instance.dll_set_diagnostic_flags(1)
xc_instance.dll_set_comm_port(1)
xc_instance.dll_start_communicating_with_timers()
xc_instance.dll_generate_dummy_record()
record = xc_instance.dll_get_next_timer_record()
for key, item in record.items():
    print(f"Key: '{key}'.  Value: '{item}'")
# srt_instance = SRT_ACQUISITION_DLL()
# srt_instance.dll_initialize_dll_task(0,"Z:/home/tim/Documents/Programs/NYSSRA/LIVETIMING/python")
# srt_instance.dll_set_string_delimiter(5)
# # srt_instance.dll_generate_dummy_record()
# # record = srt_instance.dll_put_timer_structure_into_fifo()
# # for field_name, _ in record._fields_:
# #     value = getattr(record, field_name)
# #     print(f"Name: '{field_name}'.  Value: '{value}'")
# print(srt_instance.dll_test_long(2,3))