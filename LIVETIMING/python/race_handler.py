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
        """
        Handles the race results from the DLL. This will be a much larger function in the future.
        Because why not, this function also happens to scan the comm ports every 5 seconds
        """
        last_scan = time.monotonic()

        while True:
            current_time = time.monotonic()
            if current_time - last_scan >= 5:
                self._rescan_comm_ports()
                last_scan = current_time


            time.sleep(0.05)

    def _rescan_comm_ports(self):
        """
        This will always return an empty list when using Wine.
        As I progress, the less feasible using Wine to develop the whole thing seems.
        """
        ports = [comport.device for comport in serial.tools.list_ports.comports()]
        # FIXME: Actually implement this later. 
        

    def load_startlist(self, startlist: list):
        """
        Loads a startlist into memory.

        Args:
            startlist (list): The startlist, typically sent from the JS to `render.py`
        """
        self.logger.debug(startlist)
        self.startlist = startlist