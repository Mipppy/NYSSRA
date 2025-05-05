import logging
import threading
import time
import serial.tools.list_ports

class DLL_Race_Handler:
    def __init__(self):
        from instances import Instances 
        self.xc_timer_dll = Instances.xc_timer_dll
        self.logger = logging.getLogger("BART2")
        self.race_results_thread = threading.Thread(target=self._race_results_worker, daemon=True)
        self.race_results_thread.start()
        self.startlist = []

    def _race_results_worker(self):
        last_scan = time.monotonic()

        while True:
            current_time = time.monotonic()
            if current_time - last_scan >= 5:
                self._rescan_comm_ports()
                last_scan = current_time


            time.sleep(0.05)

    def _rescan_comm_ports(self):
        """ This will always return an empty list when using Wine."""
        ports = [comport.device for comport in serial.tools.list_ports.comports()]
        # FIXME: Actually implement this later. 
        

    def load_startlist(self, startlist: list):
        self.logger.debug(startlist)
        self.startlist = startlist