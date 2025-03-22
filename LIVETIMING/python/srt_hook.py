import ctypes
import os

data_dll = None

def load_dll():
    global data_dll
    dll_dir = os.path.abspath("includes")
    dll_path = os.path.join(dll_dir, "srt_data_acquisition_dll.dll")

    os.environ["PATH"] += f";{dll_dir}"

    data_dll = ctypes.WinDLL(dll_path, winmode=0)

def check_dll_loaded():
    if data_dll is None:
        raise Exception("DLL not loaded. Please call load_dll() first.")

def get_dll() -> ctypes.WinDLL:
    check_dll_loaded()  
    return data_dll