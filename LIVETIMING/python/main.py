from xc_timer import XC_TIMER_DLL
from settings import BART2_SETTINGS
from helpers import initialize_logger
from render import HTMLWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys,os,platform
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent



app = QApplication(sys.argv)
window_instance = HTMLWindow()
window_instance.show()

def get_window() -> HTMLWindow:
    return window_instance


if platform.system() == "Windows":
    xc_instance = XC_TIMER_DLL()
    def get_xc_dll() -> XC_TIMER_DLL:
        return xc_instance


settings_instance = BART2_SETTINGS()

def get_settings() -> BART2_SETTINGS:
    return settings_instance

logger_instance = initialize_logger(bool(settings_instance.get_setting("VERBOSE_LOGGING")),window_provider=window_instance)
logger_instance.info("Successfully initialized!")


sys.exit(app.exec_())
# xc_instance.dll_initialize_dll_task(0x110, 'srt/')
# xc_instance.dll_set_comm_port(2)
# xc_instance.dll_set_diagnostic_flags(1)
# xc_instance.dll_set_string_delimiter(0)
# xc_instance.dll_generate_dummy_record()
# record = xc_instance.dll_get_next_timer_record()
# for key,item in record.items():
#     print(f"Key: {key}  - Value: {item}")