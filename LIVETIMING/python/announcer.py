import logging
import pyttsx3
import threading
import time



class Announcer:
    """
    Announcer fails to run on Wine because of a comtypes error with it not being able to generate the correct bindings. 
    """
    pass
    # def __init__(self):
    #     self.logger = logging.getLogger("BART2")
    #     self.logger.info("Successfully loaded Announcer.")
        
    #     self.engine = pyttsx3.init()
    #     self.load_settings()
    #     self.messages_to_speak = []
    #     self.lock = threading.Lock()
        
    #     self.tts_thread = threading.Thread(target=self._run_tts, daemon=True)
    #     self.tts_thread.start()

    # def _run_tts(self):
    #     while True:
    #         message = None
    #         with self.lock:
    #             if self.messages_to_speak:
    #                 message = self.messages_to_speak.pop(0)

    #         if message:
    #             self.engine.say(message)
    #             self.engine.runAndWait()
    #         else:
    #             time.sleep(0.25)

    # def handle_incoming_result(self, result):
    #     # TODO: Implement this later once we get data from DLLs
    #     with self.lock:
    #         self.messages_to_speak.append(result)

    # def load_settings(self):
    #     from instances import Instances
    #     tts_volume = Instances.settings.get_setting("TTS_VOLUME")
    #     tts_rate = Instances.settings.get_setting("TTS_RATE")
    #     tts_male = bool(Instances.settings.get_setting("TTS_MALE"))
        
    #     voices = self.engine.getProperty("voices")
    #     self.engine.setProperty("voice", voices[0 if tts_male else 1].id)
    #     self.engine.setProperty("rate", tts_rate)
    #     self.engine.setProperty("volume", tts_volume)