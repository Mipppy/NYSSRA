import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView #type: ignore
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWebChannel import QWebChannel
import logging
from typing import List
import json


class Bridge(QObject):
    js_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._messages = []
        
    @pyqtSlot(str)
    def py_message(self, msg: str):
        """Handle messages from JavaScript with proper error handling and logging."""
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
            
            if message_type == "ready":
                logger.info("JavaScript connection initialized")
                self.js_initialized = True  
            elif message_type == "livetiming_form":
                from instances import Instances
                Instances.livetiming.reinit()
                Instances.livetiming.connect_to_livetiming_ws()
                Instances.livetiming.send_auth_and_config(json_msg['data'])
            elif message_type == "give_me_the_fucking_password":
                from instances import Instances
                password = Instances.settings.get_setting("SAVED_PASSWORD")
                self.send_to_js(f"SAVED_PASSWORD|||{password}")
            else:
                logger.warning(f"Unhandled message type: {message_type}")
                
        except Exception as e:
            logger.exception(f"Unexpected error processing message: {e}")
                
        
    def send_to_js(self, message):
        self.js_message.emit(str(message))

class HTMLWindow(QMainWindow):
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
        from instances import Instances
        Instances.livetiming.reinit()
        a0.accept()
    
    def load_html(self, file_path):
        html = Path(file_path).read_text(encoding="utf8")
        base_url = QUrl.fromLocalFile(str(Path(file_path).absolute()))
        self.browser.setHtml(html, base_url)
    
    def send_test_message(self,message):
        self.bridge.send_to_js(message)

def create_window() -> List[QApplication|HTMLWindow]:
    app = QApplication(sys.argv)
    window = HTMLWindow()
    window.show()
    return [app,window]
