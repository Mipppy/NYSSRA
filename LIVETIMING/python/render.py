import sys
from pathlib import Path
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow #type: ignore
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings #type: ignore
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, QTimer #type:ignore
from PyQt5.QtWebChannel import QWebChannel #type: ignore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import logging
from typing import List
from pathlib import Path
import json
from helpers import openFileInExplorer, create_needed_dirs, get_root_documents_folder


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

            # logger.debug(f"Raw message from JS: {msg}")
            
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
                self.initalBridgeMessages()
            elif message_type == "give_me_the_fucking_password":
                password = Instances.settings.get_setting("SAVED_PASSWORD")
                if not int(Instances.settings.get_setting("SAVE_PASSWORD")):
                    password = ''
                self.send_to_js(f"SAVED_PASSWORD|||{password}")
                logger.debug("Sent saved password to window.")
            elif message_type == "startlist_input2":
                Instances.dll_interfacer.load_startlist(json_msg['data'])
            elif message_type == "open_file":
                openFileInExplorer(json_msg['data'])
            elif message_type == "open_folder":
                openFileInExplorer(get_root_documents_folder())
            elif message_type == "change_settings":
                Instances.settings.update_settings_from_window(json_msg['data'])
            elif message_type == "gimmie_settings":
                settings_dict = Instances.settings.get_all_settings()
                self.send_to_js(f"SETTINGS|||{json.dumps(settings_dict)}")
                logger.debug("Sent settings to window.")
            elif message_type == "reset_settings":
                Instances.settings.load_defaults()
            elif message_type == "start_race":
                Instances.dll_interfacer.start_race(json_msg["data"])
                self.send_to_js(f'STARTED_RACE_SUCCESSFULLY|||{json_msg['data']}')
            elif message_type == "kill_race":
                Instances.dll_interfacer.kill_race()
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
        
    def initalBridgeMessages(self):
        """
        Creates messages to JS once the bridge is open.
        """
        from instances import Instances
        self.send_to_js(f"VERSION_NUMBER|||{Instances.settings.VERSION_NUMBER}")
        self.send_to_js(f"LOCAL_WEB_SERVER|||{Instances.local_web_server.local_ip_addr}")
class MyWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Just logging it crashes the program with no error.
        QTimer.singleShot(0, lambda: (
            (lambda log_func: log_func(f"[JS] {message} (line {lineNumber})"))(
                {
                    0: logging.getLogger("BART2").debug,
                    1: logging.getLogger("BART2").warning,
                    2: logging.getLogger("BART2").error  
                }.get(level, logging.getLogger("BART2").debug)
            )
        ))

class HTMLWindow(QMainWindow):
    """
    The actual window class.
    It uses HTML/JS rendering because as much as I hate CSS, I greatly prefer it to working with 
    Qt's shitty formatting for it's elements.

    7 Months later, I regret this choice.
    Fuck 'em both
    
    Args:
        QMainWindow : A QMainWindow
    """
    bridge: Bridge
    def __init__(self, html_file='rendering/index.html'):
        super().__init__()
        self.setWindowTitle("Timing System")
        self.browser = QWebEngineView()
        self.browser.setPage(MyWebEnginePage(self.browser))
        self.setCentralWidget(self.browser)
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject('bridge', self.bridge)
        self.browser.page().setWebChannel(self.channel)
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(screen.width() , screen.height())  
        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.load_html(html_file)
        QTimer.singleShot(0, lambda: self.setGeometry(QApplication.primaryScreen().availableGeometry()))

    def closeEvent(self, a0):
        """
        When the window is closed, this closes the Websocket as well.  
        Without this, the websocket can live on indefinitely in the background.

        Args:
            a0 (QCloseEvent): This is passed by Qt.  Oddly, naming the variable anything other than it's generated named, a0, creates errors or issues with VS code
        """
        from instances import Instances
        Instances.dll_interfacer.kill_race()
        Instances.livetiming.reinit()
        Instances.local_web_server.httpd.shutdown()
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
    create_needed_dirs()
    app = QApplication(sys.argv)
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = HTMLWindow()
    window.show()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    return [app,window]
