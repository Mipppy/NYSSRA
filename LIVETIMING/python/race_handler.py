import logging
import threading
import time
from xc_timer import XC_TIMER_DLL
import csv 
from datetime import datetime
import serial.tools.list_ports #type:ignore
from typing import List
import base64
import json
from io import BytesIO,StringIO
import openpyxl
import csv
class DLL_Race_Handler:
        # The class for overall timer records, with our startlist data + the timer record provided by the DLL.
    class BatchedTimerRecord:
        def __init__(self, bib_num: str | None, first_name: str | None, last_name: str | None, team:str | None, dll_record_structure: XC_TIMER_DLL.XC_TIMER_RECORD_STRUCTURE_TYPE, additional_startlist_data: dict | None):
            self.bib_num = bib_num
            self.first_name = first_name
            self.last_name = last_name
            self.team = team
            self.dll_record_structure = dll_record_structure
            self.additional_startlist_data = additional_startlist_data

    def __init__(self):
        
        from instances import Instances 
        self.xc_timer_dll = Instances.xc_timer_dll
        # It feels a little wrong initializing the DLL here, but whatever.
        self.xc_timer_dll.dll_initialize_dll_task(0x100 | 0x40 | 0x10 | 2,'srt/')
        self.xc_timer_dll.dll_set_string_delimiter(0)
        self.startlist: List[dict] = []
        self.currently_active_race_data: List[DLL_Race_Handler.BatchedTimerRecord] = []
        self.serial_comm_ports = []
        self.is_currently_racing = False
        self.startlist_file_type = "csv"
        self.startlist_file_name = "unknown"
        self.logger = logging.getLogger("BART2")
        self.race_results_thread = threading.Thread(target=self._race_results_worker, daemon=True)
        self.race_results_thread.start()
        # Startlist should always at least have one participant with at least this dict data
        # {"bib_num": int, "first_name": str, "last_name": str, "team": str}


    def _race_results_worker(self):
        """
        Handles the race results from the DLL. This will be a much larger function in the future.
        Because why not, this function also happens to scan the comm ports every 5 seconds
        """
        last_scan = time.monotonic()

        while True:
            # Rescanning for serial communication ports
            current_time = time.monotonic()
            if current_time - last_scan >= 5:
                self._rescan_comm_ports()
                last_scan = current_time
                
            if self.is_currently_racing:
                while True:
                    timer_record = self.xc_timer_dll.dll_get_next_timer_structure()
                    if not timer_record:
                        break
                    print(timer_record)

            # !!! ~50ms clock !!!
            time.sleep(0.05)

    def _handle_timer_record(self, record: XC_TIMER_DLL.XC_TIMER_RECORD_STRUCTURE_TYPE) -> BatchedTimerRecord | None:
        if self.startlist == []:
            self.logger.error("Attempted to handle incoming timer record without startlist!")
    
        from instances import Instances
        if Instances.settings.get_setting("USE_PC_TIME") == 1:
            if record.record_typ == 'b':
                racer = next((p for p in self.startlist if p["bib_num"] == record.bib_string), None)
                racer.pop('bib_num', None)
                active_batched_record = self.BatchedTimerRecord(
                    bib_num=record.bib_string,
                    first_name=racer.pop('first_name', None),
                    last_name=racer.pop('last_name', None), 
                    team=racer.pop('team', None),
                    dll_record_structure=record,
                    additional_startlist_data=racer
                )
                record.timer_time = datetime.strptime(record.timer_time, "%H:%M:%S.%f")
                record.pc_time = datetime.strptime(record.pc_time, "%H:%M:%S")
                self.currently_active_race_data.append(active_batched_record)
                return active_batched_record
        return None         
    
    def generate_results_csv(self, verbose: bool = False) -> str | None:
        
        if not self.currently_active_race_data:
            self.logger.error('There is no race data to generate the results file with.')
            return None

        if self.is_currently_racing:
            self.logger.error('Cannot generate a results file while a race is still going.')
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"race_results_{timestamp}.csv"

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                if not verbose:
                    writer.writerow(["PLACE", "BIB", "NAME", "AGE", "TEAM", "PC_TIME"])
                    for place, record in enumerate(self.currently_active_race_data, start=1):
                        dll_rec = record.dll_record_structure
                        pc_time = (
                            dll_rec.pc_time.strftime("%H:%M:%S")
                            if isinstance(dll_rec.pc_time, datetime)
                            else dll_rec.pc_time
                        )
                        name = f"{record.last_name}, {record.first_name}".strip(", ")
                        age = None
                        if record.additional_startlist_data:
                            age = record.additional_startlist_data.get("age")
                        writer.writerow([
                            place,
                            record.bib_num or "",
                            name,
                            age if age is not None else "",
                            record.team or "",
                            pc_time
                        ])

                else:
                    header_written = False
                    for place, record in enumerate(self.currently_active_race_data, start=1):
                        dll_rec = record.dll_record_structure
                        row_dict = dll_rec.as_dict()

                        row_dict = {
                            "place": place,
                            "bib_num": record.bib_num,
                            "first_name": record.first_name,
                            "last_name": record.last_name,
                            "team": record.team,
                            **(record.additional_startlist_data or {}),
                            **row_dict,
                        }

                        if not header_written:
                            writer.writerow(row_dict.keys())
                            header_written = True

                        writer.writerow(row_dict.values())

            self.logger.info(f"Results CSV generated: {filename}")
            return filename

        except Exception as e:
            self.logger.error(f"Failed to generate results CSV: {e}")
            return None



    def _rescan_comm_ports(self):
        """
        This will always return an empty list when using Wine.
        As I progress, the less feasible using Wine to develop the whole thing seems.
        """
        self.serial_comm_ports = serial.tools.list_ports.comports()
            
        from instances import Instances
        Instances.window.bridge.send_to_js(f"SERIAL_COM_PORTS|||{json.dumps({'ports': [[port.device, port.manufacturer] for port in self.serial_comm_ports]})}")

    def load_startlist(self, startlist_data: dict):
        b64 = startlist_data.get("file_data", "")
        file_bytes = base64.b64decode(b64)

        self.startlist_file_type = startlist_data.get("file_type", "")
        self.startlist_file_name = startlist_data.get("file_name", "")


        if self.startlist_file_name.endswith(".csv"):
            decoded = file_bytes.decode("utf-8", errors="ignore")
            reader = csv.DictReader(StringIO(decoded))
            self.startlist = list(reader)

        elif self.startlist_file_name.endswith(".xls") or self.startlist_file_name.endswith(".xlsx"):


            buf = BytesIO(file_bytes)
            wb = openpyxl.load_workbook(buf)
            ws = wb.active

            rows = []
            for row in ws.iter_rows(values_only=True):
                rows.append(row)

            self.startlist = [list(row) for row in rows]
        from instances import Instances
        Instances.window.bridge.send_to_js(f"STARTLIST_DATA|||{json.dumps({'data': self.startlist})}")    
    def start_race(self, comm_port: int, event: int, heat: int) -> int:
        """
        Starts a race.

        Args:
            comm_port (int): The communication port where the modem is plugged in.
            event (int) / heat (int): Both aren't needed, and can really be set it whatever value, it doesn't matter.
        """
        if self.startlist:
            self.xc_timer_dll.dll_set_comm_port(comm_port)
            self.xc_timer_dll.dll_start_communicating_with_timers()
            self.xc_timer_dll.dll_set_event_and_heat(0, event, heat)
            self.xc_timer_dll.dll_synch_timers(0,"0")
            self.is_currently_racing = True
            return 0
        else:
            # If you don't have a startlist, we aren't letting you start a race.
            return -1
        
    def end_race(self):
        self.xc_timer_dll.dll_stop_communicating_with_timers()
        # Other cleanup later.
