import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWebChannel import QWebChannel
import logging

class Bridge(QObject):
    js_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._messages = []
        
    @pyqtSlot(str)
    def py_message(self, msg):
        print(f"From JS: {msg}")
        if msg == "ready":  
            logging.getLogger('BART2').info('Javascript connection initialized.')
            
        
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
        
        self.load_html(html_file)
        
    
    def load_html(self, file_path):
        html = Path(file_path).read_text(encoding="utf8")
        base_url = QUrl.fromLocalFile(str(Path(file_path).absolute()))
        self.browser.setHtml(html, base_url)
    
    def send_test_message(self,message):
        self.bridge.send_to_js(message)

def main():
    app = QApplication(sys.argv)
    window = HTMLWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()