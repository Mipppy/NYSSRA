from xc_timer import XC_TIMER_DLL
import random

instance = XC_TIMER_DLL()
instance.dll_initialize_dll_task(0x110,'srt/')
instance.dll_set_comm_port(3)
instance.dll_set_number_of_timers(1)
instance.dll_start_communicating_with_timers()
instance.dll_set_event_and_heat(0, 3, 5)

while True:
    d = instance.dll_get_next_timer_record()
    if d:
        print(d)
    if random.randint(0,10000) == 50:
        instance.dll_generate_dummy_record()
    instance.dll_synch_timers(0,"")