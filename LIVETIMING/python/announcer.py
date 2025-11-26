import logging
import threading
import time
import pyttsx3
import queue

class Announcer:
    """
    Threaded TTS announcer that works for both rapid and spaced-out messages.
    """
    def __init__(self):
        self.logger = logging.getLogger("BART2")
        self.logger.info("Successfully loaded Announcer.")

        self.engine = pyttsx3.init()
        self.load_settings()

        self.messages_to_speak = queue.Queue()
        self._stop_event = threading.Event()

        self.tts_thread = threading.Thread(target=self._run_tts, daemon=True)
        self.tts_thread.start()

    def _run_tts(self):
        """
        Continuously processes messages in the queue.
        """
        while not self._stop_event.is_set():
            try:
                # Block briefly for new messages
                message = self.messages_to_speak.get(timeout=0.2)
                print(message)
                self.engine.say(message)
                self.engine.runAndWait()
            except queue.Empty:
                # No messages, just wait and loop again
                time.sleep(0.05)
            except Exception as e:
                self.logger.error(f"TTS engine error: {e}")

    def handle_incoming_result(self, result):
        """
        Queue a new message to be spoken.
        """
        message_to_speak = f"{result.first_name} {result.last_name}"
        print(message_to_speak)
        self.messages_to_speak.put(message_to_speak)

    def load_settings(self):
        from instances import Instances
        tts_volume = Instances.settings.get_setting("TTS_VOLUME") or 1.0
        tts_rate = Instances.settings.get_setting("TTS_RATE") or 150
        tts_male = bool(Instances.settings.get_setting("TTS_MALE"))

        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0 if tts_male else 1].id)
        self.engine.setProperty("rate", tts_rate)
        self.engine.setProperty("volume", tts_volume)

    def stop(self):
        """
        Stop the TTS thread gracefully.
        """
        self._stop_event.set()
        self.tts_thread.join()
