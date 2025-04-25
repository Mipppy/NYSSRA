from render import create_window
from xc_timer import XC_TIMER_DLL
from settings import BART2_SETTINGS
from helpers import initialize_logger
from comms import ServerCommunications
# I WISH I HAD POINTERS

class Instances:
    # Set to None here to enable autocomplete on most IDEs
    window = None
    window_app = None
    xc_timer_dll = None
    settings = None
    logger = None
    @classmethod
    def create_instances(cls):
            print("CALLED")
            window_list = create_window()
            cls.window = window_list[1]
            cls.window_app = window_list[0]
            cls.xc_timer_dll = XC_TIMER_DLL()
            cls.settings = BART2_SETTINGS()
            cls.communications = ServerCommunications()
            cls.logger = initialize_logger(
                bool(cls.settings.get_setting("VERBOSE_LOGGING")),
                window_provider=cls.window
            )
            cls.logger.info("All classes successfully initialized.")

# Instances = _Instances
# settings = _Instances.settings
# window = _Instances.window
# xc_timer_dll = _Instances.xc_timer_dll

