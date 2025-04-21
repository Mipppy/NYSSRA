"""
To run:
 **Windows** - `python main.py`
 **Linux** - `wine python main.py`   (Tested with: Fedora)
"""

import sys
from instances import Instances


Instances.create_instances()




sys.exit(Instances.window_app.exec_())
# xc_instance.dll_initialize_dll_task(0x110, 'srt/')
# xc_instance.dll_set_comm_port(2)
# xc_instance.dll_set_diagnostic_flags(1)
# xc_instance.dll_set_string_delimiter(0)
# xc_instance.dll_generate_dummy_record()
# record = xc_instance.dll_get_next_timer_record()
# for key,item in record.items():
#     print(f"Key: {key}  - Value: {item}")