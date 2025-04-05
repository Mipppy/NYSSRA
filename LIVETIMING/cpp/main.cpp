#include <windows.h>
#include <iostream>

typedef int (__stdcall *DLL_INIT_TASK)(long, long);  // Change char* to const char*

int main() {
    HMODULE hDLL = LoadLibrary("Z:\\home\\tim\\Documents\\Programs\\NYSSRA\\LIVETIMING\\cpp\\lib\\srt_data_acquisition_dll.dll");;
    if (!hDLL) {
        std::cerr << "Failed to load DLL!" << std::endl;
        return 1;
    }

    // Get function address
    DLL_INIT_TASK dll_initialize_dll_task = (DLL_INIT_TASK)GetProcAddress(hDLL, "dll_test_function_call_passing_long");
    if (!dll_initialize_dll_task) {
        std::cerr << "Failed to load function from DLL!" << std::endl;
        FreeLibrary(hDLL);
        return 1;
    }

    // Call function with correct type
    dll_initialize_dll_task((long) 2, (long) 3);

    FreeLibrary(hDLL);
    return 0;
}
