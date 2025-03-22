#include <iostream>
#include <windows.h>

// Declare the function pointer type for the function we expect from the DLL
typedef void (*dll_set_comm_port_t)(const char*);

class SrtHook {
private:
    // Function pointer for the DLL function
    dll_set_comm_port_t dll_set_comm_port;

public:
    SrtHook() : dll_set_comm_port(nullptr) {
        // DLL is expected to be loaded dynamically
        // Here we use LoadLibraryA to load the DLL at runtime
        HINSTANCE dllHandle = LoadLibraryA("srt_data_acquisition_dll.dll");

        if (dllHandle) {
            // Initialize the function pointer using GetProcAddress
            dll_set_comm_port = reinterpret_cast<dll_set_comm_port_t>(GetProcAddress(dllHandle, "dll_set_comm_port"));

            if (!dll_set_comm_port) {
                std::cerr << "Failed to find the function in the DLL!" << std::endl;
            }
        } else {
            std::cerr << "Failed to load the DLL!" << std::endl;
        }
    }

    bool is_dll_loaded() {
        return dll_set_comm_port != nullptr;
    }

    void set_comm_port(const char* comm_port) {
        if (!is_dll_loaded()) {
            std::cerr << "DLL function is not linked properly!" << std::endl;
            return;
        }

        dll_set_comm_port(comm_port);
    }
};

int main() {
    SrtHook srtHook;
    
    if (srtHook.is_dll_loaded()) {
        const char* commPort = "COM1";
        srtHook.set_comm_port(commPort);
        std::cout << "Communication port set to " << commPort << std::endl;
    } else {
        std::cerr << "Failed to load the DLL function!" << std::endl;
    }

    return 0;
}
