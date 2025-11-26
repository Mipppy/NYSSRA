from datetime import datetime, timedelta
import math
import threading
from xc_timer import XC_TIMER_DLL
import time
import random
from typing import List
import serial.tools.list_ports
import json
import csv
from io import StringIO, BytesIO
import openpyxl
import logging
import base64
from pathlib import Path
from helpers import get_race_internals_folder


class Alt_Race_Handler:
    class BatchedTimerRecord:
        def __init__(
            self,
            bib_num: str | None,
            first_name: str | None,
            last_name: str | None,
            team: str | None,
            dll_record_structure: dict,
            additional_startlist_data: dict | None,
            timing_data: dict,
        ):
            self.bib_num = bib_num
            self.first_name = first_name
            self.last_name = last_name
            self.team = team
            self.dll_record_structure = dll_record_structure
            self.additional_startlist_data = additional_startlist_data
            self.timing_data = timing_data

        def __str__(self):
            return f"BatchedTimerRecord({self.__dict__})"

        def to_dict(self):
            def serialize_td(td):
                if isinstance(td, timedelta):
                    return td.total_seconds()
                return td

            return {
                "bib_num": self.bib_num,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "team": self.team,
                "dll_record_structure": self.dll_record_structure,
                "additional_startlist_data": self.additional_startlist_data,
                "timing_data": {
                    k: serialize_td(v) for k, v in self.timing_data.items()
                },
            }

    def __init__(self):
        self.xc_timer_dll = XC_TIMER_DLL()
        self.startlist: List[dict] = []
        self.startlist_parsed: List[dict] = []
        self.logger = logging.getLogger("BART2")
        self.conf_data = None
        self.race_cfg_data = None
        self.global_struct = None
        self.race_officially_start = False
        self.race_loop_thread: threading.Thread = None
        self.comm_port_thread: threading.Thread = None
        self.event_heat: List[int, int] = []
        self.saved_parsed_results: List[Alt_Race_Handler.BatchedTimerRecord] = []
        self.saved_raw_results: List[dict] = []
        self.thread_shutdown_signal: bool = False

        self.comm_port_thread = threading.Thread(
            target=self._comm_port_scan_loop, daemon=True
        )
        self.comm_port_thread.start()

    def _comm_port_scan_loop(self):
        while True:
            self.serial_comm_ports = serial.tools.list_ports.comports()

            from instances import Instances

            Instances.window.bridge.send_to_js(
                f"SERIAL_COM_PORTS|||{json.dumps({'ports': [[port.device, port.manufacturer] for port in self.serial_comm_ports]})}"
            )

            time.sleep(3)

    def _race_loop(self):
        race_start_str = self.race_cfg_data.get("raceStartTime", "00:00")
        now = datetime.now()
        hour, minute = map(int, race_start_str.split(":"))
        race_start_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if race_start_dt < now:
            race_start_dt = now
        self.race_officially_start = False
        while not self.thread_shutdown_signal:
            if not self.race_officially_start and datetime.now() >= race_start_dt:
                self.race_officially_start = True
                from instances import Instances

                Instances.window.bridge.send_to_js("RACE_STARTED|||Race has started!")

            while True:
                d = self.xc_timer_dll.dll_get_character_from_terminal_fifo()
                if d == -1:
                    break
                # print("Terminal char:", chr(d) if d < 128 else d)

            while True:
                record = self.xc_timer_dll.dll_get_next_timer_structure()
                if not record:
                    break
                record_as_dict = record.as_dict()
                if record.record_typ == "b":
                    if record.heat_num == self.event_heat[1] and record.event_num == self.event_heat[0]:
                        self.saved_raw_results.append(record_as_dict)
                        self.parse_new_record(record_as_dict)


            # !!!! ~50 MS CLOCK !!!!
            time.sleep(0.05)

    def start_race(self, cfg: dict):
        if self.race_officially_start:
            self.kill_race()
        self.race_cfg_data: dict = cfg

        self.xc_timer_dll.dll_initialize_dll_task(0x100 | 0x40 | 0x10 | 2, "srt/")
        self.xc_timer_dll.dll_set_string_delimiter(0)

        self.conf_data = self.xc_timer_dll.dll_get_pointer_to_configuration_structure()
        self.global_struct = (
            self.xc_timer_dll.dll_get_pointer_to_global_variable_structure()
        )

        self.xc_timer_dll.dll_set_comm_port(3)
        self.xc_timer_dll.dll_start_communicating_with_timers()

        self.event_heat = random.sample(range(1, 8), 2)
        self.xc_timer_dll.dll_set_event_and_heat(
            0, self.event_heat[0], self.event_heat[1]
        )
        self.xc_timer_dll.dll_synch_timers(0, "0")

        from instances import Instances

        if self.race_cfg_data.get("useLivetiming"):
            Instances.livetiming.reinit()
            Instances.livetiming.connect_to_livetiming_ws()
            Instances.livetiming.send_auth_and_config(self.race_cfg_data)

        # We clear results here because we want to host the results of the previous race until the next race starts
        Instances.local_web_server.clear_results()

        self.thread_shutdown_signal = False
        self.race_loop_thread = threading.Thread(target=self._race_loop, daemon=True)
        self.race_loop_thread.start()

    def parse_new_record(self, record: dict):
        race_start_str = self.race_cfg_data.get("raceStartTime", "00:00")
        today = datetime.today()
        hour, minute = map(int, race_start_str.split(":"))
        race_start_dt = today.replace(hour=hour, minute=minute, second=0, microsecond=0)

        now = datetime.now()
        if now < race_start_dt:
            self.logger.warning(
                f"Received early record for bib {record.get('bib_string')} at {now.time()} before race start {race_start_dt.time()}"
            )
            return

        bib_num = record.get("bib_string", None)
        if bib_num is None:
            self.logger.warning("Received record without bib_string")
            return

        bib_data = self.get_racerdata_from_bib(bib_num)
        racer_data = bib_data["racer_data"]
        additional_data = bib_data["additional"]

        racer_time_data = {}

        pc = datetime.strptime(record.get("pc_time"), "%H:%M:%S")
        racer_time_data["pc_time"] = timedelta(
            hours=pc.hour, minutes=pc.minute, seconds=pc.second
        )

        tt = datetime.strptime(record.get("timer_time"), "%H:%M:%S.%f")
        racer_time_data["timer_time"] = timedelta(
            hours=tt.hour,
            minutes=tt.minute,
            seconds=tt.second,
            microseconds=tt.microsecond,
        )

        if self.race_cfg_data.get("raceType") == "1":
            bib_index = additional_data["bib_index"]
            athletes_per_wave = self.race_cfg_data["intervalStart"]["athletesPerWave"]
            interval_seconds = self.race_cfg_data["intervalStart"]["startInterval"]

            wave_index = bib_index // athletes_per_wave
            interval_time_offset = wave_index * interval_seconds

            hour, minute = map(
                int, self.race_cfg_data.get("raceStartTime", "00:00").split(":")
            )
            race_start_td = timedelta(hours=hour, minutes=minute)

            corrected_time = (
                racer_time_data["timer_time"]
                - race_start_td
                - timedelta(seconds=interval_time_offset)
            )
            if corrected_time < timedelta(0):
                corrected_time = timedelta(0)

            racer_time_data["interval_time_offset"] = interval_time_offset
            racer_time_data["corrected_time"] = corrected_time
        if racer_data is None:
            racer_data = {}
        new_parsed_record = self.BatchedTimerRecord(
            bib_num,
            racer_data.get("first_name", "Unknown"),
            racer_data.get("last_name", "Unknown"),
            racer_data.get("team", "Unknown"),
            record,
            additional_data,
            timing_data=racer_time_data,
        )
        self.logger.debug(new_parsed_record)
        self.saved_parsed_results.append(new_parsed_record)
        self.alert_other_systems_of_record(new_parsed_record)

    def alert_other_systems_of_record(self, parsed_record: BatchedTimerRecord):
        from instances import Instances

        dictified = [r.to_dict() for r in self.saved_parsed_results]
        Instances.window.bridge.send_to_js(f"UPDATED_RESULTS|||{json.dumps(dictified)}")
        Instances.announcer.handle_incoming_result(parsed_record)
        Instances.local_web_server.update_results(dictified)
        Instances.livetiming.send_json_message(dictified)

    def get_racerdata_from_bib(self, bib_num: str) -> dict:
        if not self.startlist or not self.startlist_parsed:
            return {}

        try:
            bib_num_norm = str(int(str(bib_num).strip()))
        except:
            bib_num_norm = str(bib_num).strip()

        matched_index = 0
        racer_data = None

        for idx, racer in enumerate(self.startlist_parsed):
            if racer.get("bib") is None:
                continue

            try:
                r_bib_norm = str(int(str(racer["bib"]).strip()))
            except:
                r_bib_norm = str(racer["bib"]).strip()

            if r_bib_norm == bib_num_norm:
                matched_index = idx
                racer_data = dict(racer)
                break

        header = self.startlist[0]
        row = self.startlist[matched_index]

        USED_KEYS = {
            "bib",
            "first_name",
            "last_name",
            "sex",
            "class",
            "alt_class",
            "team",
        }

        def normalize(s):
            if not s:
                return ""
            return "".join(ch for ch in str(s).upper() if ch.isalnum())

        EXPECTED_MAP = {
            "BIB": "bib",
            "BIBNUMBER": "bib",
            "BIBNO": "bib",
            "BIB#": "bib",
            "LASTNAME": "last_name",
            "SURNAME": "last_name",
            "FIRSTNAME": "first_name",
            "GIVENNAME": "first_name",
            "SEX": "sex",
            "GENDER": "sex",
            "CLASS": "class",
            "ALTCLASS": "alt_class",
            "ALTERNATECLASS": "alt_class",
            "TEAM": "team",
        }

        def map_header(h):
            n = normalize(h)
            return EXPECTED_MAP.get(n)

        additional = {}

        for i, col_name in enumerate(header):
            internal_key = map_header(col_name)

            if internal_key not in USED_KEYS:
                if i < len(row):
                    additional[col_name] = row[i]
        additional["bib_index"] = matched_index if matched_index else 0
        data = {"racer_data": racer_data, "additional": additional}

        return data

    def load_startlist(self, startlist_data: dict):
        b64 = startlist_data.get("file_data", "")
        file_bytes = base64.b64decode(b64)

        self.startlist_file_type = startlist_data.get("file_type", "")
        self.startlist_file_name = startlist_data.get("file_name", "")

        if self.startlist_file_name.endswith(".csv"):
            decoded = file_bytes.decode("utf-8", errors="ignore")
            reader = csv.reader(StringIO(decoded))
            self.startlist = [row for row in reader]

        elif self.startlist_file_name.endswith(
            ".xls"
        ) or self.startlist_file_name.endswith(".xlsx"):
            buf = BytesIO(file_bytes)
            wb = openpyxl.load_workbook(buf)
            ws = wb.active
            self.startlist = [list(row) for row in ws.iter_rows(values_only=True)]

        if not self.startlist:
            return

        header_row = self.startlist[0]

        def normalize(s):
            """str → normalized key (remove spaces, #, punctuation, uppercase)."""
            if not s:
                return ""
            return "".join(ch for ch in s.upper() if ch.isalnum())

        normalized_header_map = {normalize(h): i for i, h in enumerate(header_row)}

        EXPECTED = {
            "BIB": "bib",
            "BIBNUMBER": "bib",
            "BIBNO": "bib",
            "BIB#": "bib",
            "LASTNAME": "last_name",
            "SURNAME": "last_name",
            "FIRSTNAME": "first_name",
            "GIVENNAME": "first_name",
            "SEX": "sex",
            "GENDER": "sex",
            "CLASS": "class",
            "ALTCLASS": "alt_class",
            "ALTERNATECLASS": "alt_class",
            "TEAM": "team",
        }

        def match_key(nkey):
            for norm_compare, internal in EXPECTED.items():
                if nkey == norm_compare:
                    return internal
            return None

        self.startlist_parsed = []

        for row in self.startlist[1:]:
            racer = {
                "bib": None,
                "last_name": None,
                "first_name": None,
                "sex": None,
                "class": None,
                "alt_class": None,
                "team": None,
            }

            for norm_header, col_index in normalized_header_map.items():
                internal = match_key(norm_header)
                if internal and col_index < len(row):
                    racer[internal] = row[col_index]

            self.startlist_parsed.append(racer)

        from instances import Instances

        Instances.window.bridge.send_to_js(
            f"STARTLIST_DATA|||{json.dumps({'data': self.startlist})}"
        )


    def save_results_info(self):
        base_folder = get_race_internals_folder()
        race_name = self.race_cfg_data.get("raceName", "Race")

        safe_race_name = "".join(
            c for c in race_name if c.isalnum() or c in (" ", "_", "-")
        ).strip()

        date_str = datetime.now().strftime("%m-%d-%Y")
        folder_name = f"{date_str}_{safe_race_name}"

        result_folder = base_folder / folder_name
        result_folder.mkdir(parents=True, exist_ok=True)

        try:
            cfg_path = result_folder / "race_config.json"
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(self.race_cfg_data, f, indent=4)
            self.logger.debug(f"Saved race config -> {cfg_path}")
        except Exception as e:
            self.logger.error(f"Failed to save race config: {e}")

        try:
            startlist_path = result_folder / "startlist.csv"
            with open(startlist_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for row in self.startlist:
                    writer.writerow(row)
            self.logger.debug(f"Saved startlist -> {startlist_path}")
        except Exception as e:
            self.logger.error(f"Failed to save startlist: {e}")

        try:
            results_path = result_folder / "race_results.json"
            parsed = [r.to_dict() for r in self.saved_parsed_results]
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=4)
            self.logger.debug(f"Saved race results -> {results_path}")
        except Exception as e:
            self.logger.error(f"Failed to save race results: {e}")

        return result_folder

    def save_results_pdf(self):
        pass

    def kill_race(self):
        # Most of the cleanup is done when a new race is started.
        self.thread_shutdown_signal = True
        self.race_officially_start = False
        self.saved_parsed_results = []
        self.saved_raw_results = []
        from instances import Instances

        Instances.announcer.clear_talk_pool()
        Instances.livetiming.reinit()
        res_folder = self.save_results_info()
        Instances.window.bridge.send_to_js(f"RACE_OVER|||{res_folder}")
