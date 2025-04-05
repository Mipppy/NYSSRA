from srt_hook import SRT_DLL
from ctypes import *


srt_instance = SRT_DLL()
srt_instance.dll_initialize_dll_task(0,"Z:/home/tim/Documents/Programs/NYSSRA/LIVETIMING/python")
srt_instance.dll_generate_dummy_record()
print(srt_instance.dll_get_next_timer_structure_from_fifo())
print(srt_instance.dll_test_long(2,3))