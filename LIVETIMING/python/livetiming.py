from srt_hook import SRT_DLL
from ctypes import *


srt_instance = SRT_DLL()
print(srt_instance.dll_test_long(2,3))