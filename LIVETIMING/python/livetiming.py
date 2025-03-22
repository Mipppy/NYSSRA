import srt_hook
import ctypes

srt_hook.load_dll()

dll = srt_hook.get_dll()
dll.dll_get_version.argtypes = []
dll.dll_get_version.restype = ctypes.c_void_p  # Use void* to avoid crashes

# Call the function and decode the result safely
version_ptr = dll.dll_get_version()
if version_ptr:
    version = ctypes.cast(version_ptr, ctypes.c_char_p).value
    print(f"DLL Version: {version.decode()}")
else:
    print("Failed to retrieve DLL version.")
