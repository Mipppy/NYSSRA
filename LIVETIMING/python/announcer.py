import logging
import threading
import time 
import pyttsx3
from race_handler import Alt_Race_Handler

class Announcer:
    
    """
    Announcer fails to run on Wine because of a comtypes error with it not being able to generate the correct bindings. 
    """
    def __init__(self):
        self.logger = logging.getLogger("BART2")
        self.logger.info("Successfully loaded Announcer.")
        
        self.engine = pyttsx3.init()
        self.load_settings()
        self.messages_to_speak = []
        self.lock = threading.Lock()
        
        self.tts_thread = threading.Thread(target=self._run_tts, daemon=True)
        self.tts_thread.start()

    def _run_tts(self):
        while True:
            messages_to_process = []
            with self.lock:
                if self.messages_to_speak:
                    messages_to_process = self.messages_to_speak[:]
                    self.messages_to_speak.clear()

            if messages_to_process:
                for message in messages_to_process:
                    self.engine.say(message)
                self.engine.runAndWait()
            else:
                time.sleep(0.1)

    def handle_incoming_result(self, result:Alt_Race_Handler.BatchedTimerRecord):
        message_to_speak = f"{result.first_name} {result.last_name}"
        with self.lock:
            self.messages_to_speak.append(message_to_speak)

    def load_settings(self):
        """
        Update voice on the fly if settings are changed.
        """
        from instances import Instances
        tts_volume = Instances.settings.get_setting("TTS_VOLUME")
        tts_rate = Instances.settings.get_setting("TTS_RATE")
        tts_male = bool(Instances.settings.get_setting("TTS_MALE"))
        
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0 if tts_male else 1].id)
        self.engine.setProperty("rate", tts_rate)
        self.engine.setProperty("volume", tts_volume)