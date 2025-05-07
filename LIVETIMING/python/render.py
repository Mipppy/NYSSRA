import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView #type: ignore
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWebChannel import QWebChannel
import logging
from typing import List
import json
from helpers import openFileInExplorer


class Bridge(QObject):
    """
    Creates a connection between the HTML/JS based window and the Python side of the program.

    Args:
        QObject: Man I don't even know what a QObject is, I just know it does what I want
    """
    js_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._messages = []
        
    @pyqtSlot(str)
    def py_message(self, msg: str):
        """Handle messages from JavaScript with proper error handling and logging (Not)."""
        logger = logging.getLogger('BART2')
        
        try:
            if not msg or not isinstance(msg, str):
                logger.warning(f"Received empty or invalid message: {msg}")
                return

            logger.debug(f"Raw message from JS: {msg}")
            
            try:
                json_msg = json.loads(msg)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON message: {e}\nMessage: {msg}")
                return

            if not isinstance(json_msg, dict):
                logger.error(f"Expected dictionary but got {type(json_msg)}: {json_msg}")
                return

            message_type = json_msg.get('message_type')
            from instances import Instances
            if message_type == "ready":
                logger.info("JavaScript connection initialized")
                self.js_initialized = True  
            elif message_type == "livetiming_form":
                Instances.livetiming.reinit()
                Instances.livetiming.connect_to_livetiming_ws()
                Instances.livetiming.send_auth_and_config(json_msg['data'])
            elif message_type == "give_me_the_fucking_password" and int(Instances.settings.get_setting("SAVE_PASSWORD")):
                password = Instances.settings.get_setting("SAVED_PASSWORD")
                self.send_to_js(f"SAVED_PASSWORD|||{password}")
                logger.debug("Sent saved password to window.")
            elif message_type == "startlist_input":
                Instances.dll_interfacer.load_startlist(json_msg['data'])
            elif message_type == "open_file":
                openFileInExplorer(json_msg['data'])
            elif message_type == "change_setting":
                Instances.settings.update_setting_from_window(json_msg['data'])
            else:   
                logger.warning(f"Unhandled message type: {message_type}")
                
        except Exception as e:
            logger.exception(f"Unexpected error processing message: {e}")
                
        
    def send_to_js(self, message):
        """
        The function that other files can call to send messages to the HTML/JS

        Args:
            message (any): This can be anything, but it will be turned into a `str` regardless. It is the message to send.
        """
        self.js_message.emit(str(message))

class HTMLWindow(QMainWindow):
    """
    The actual window class.
    It uses HTML/JS rendering because as much as I hate CSS, I greatly prefer it to working with 
    Qt's shitty formatting for it's elements.

    Args:
        QMainWindow : A QMainWindow
    """
    def __init__(self, html_file='rendering/index.html'):
        super().__init__()
        self.setWindowTitle("Timing System")
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject('bridge', self.bridge)
        self.browser.page().setWebChannel(self.channel)
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(screen.width() , screen.height())  
        
        self.load_html(html_file)
        
    def closeEvent(self, a0):
        """
        When the window is closed, this closes the Websocket as well.  
        Without this, the websocket can live on indefinitely in the background.

        Args:
            a0 (QCloseEvent): This is passed by Qt.  Oddly, naming the variable anything other than it's generated named, a0, creates errors or issues with VS code
        """
        from instances import Instances
        Instances.livetiming.reinit()
        a0.accept()
    
    def load_html(self, file_path):
        """
        I don't even remember writing this and you'll probably never need this.

        Args:
            file_path (any): Pass whatever you want to this.  It'll probably crash anyway.
        """
        html = Path(file_path).read_text(encoding="utf8")
        base_url = QUrl.fromLocalFile(str(Path(file_path).absolute()))
        self.browser.setHtml(html, base_url)
    
    def send_test_message(self,message):
        """
        This was made during my frantic coding trying to get the window working with the `Bridge`,
        and I don't feel like deleting it.  Just use `WINDOW_INSTANCE.bridge.send_to_js()`.

        Args:
            message (any): Just never use this lets be real.
        """
        self.bridge.send_to_js(message)

def create_window() -> List[QApplication|HTMLWindow]:
    """
    Used in `instances.py` to create the window and the application, which should probably be the same thing.
    Take notes Qt.

    Returns:
        List[QApplication|HTMLWindow]: Returns both because Qt decided to make the QApplication needed for one line of code outside this file.
    """
    app = QApplication(sys.argv)
    window = HTMLWindow()
    window.show()
    return [app,window]
