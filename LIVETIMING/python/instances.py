from render import create_window
from xc_timer import XC_TIMER_DLL
from settings import BART2_SETTINGS
from helpers import initialize_logger
from comms import LivetimingHandler
from race_handler import DLL_Race_Handler
from announcer import Announcer
# I WISH I HAD POINTERS

class Instances:
    # Set to None here to enable autocomplete on Visual Studio Code, as it doesn't autocomplete for @classmethods for some reason.
    window = None
    window_app = None
    xc_timer_dll = None
    settings = None
    logger = None
    @classmethod
    def create_instances(cls):
            window_list = create_window()
            cls.settings = BART2_SETTINGS()
            cls.window = window_list[1]
            cls.logger = initialize_logger(
                bool(cls.settings.get_setting("VERBOSE_LOGGING")),
                window_provider=cls.window
            )
            cls.window_app = window_list[0]
            cls.xc_timer_dll = XC_TIMER_DLL()
            cls.livetiming = LivetimingHandler()
            cls.dll_interfacer = DLL_Race_Handler()
            cls.announcer = Announcer()
            cls.logger.info("Successfully loaded all classes.")

# Instances = _Instances
# settings = _Instances.settings
# window = _Instances.window
# xc_timer_dll = _Instances.xc_timer_dll

