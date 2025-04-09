import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class HTMLWindow(QMainWindow):
    def __init__(self, html_file='rendering/index.html'):
        super().__init__()
        self.setWindowTitle("𝗧𝗶𝗺ing System")
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        self.load_html(html_file)

    def load_html(self, file_path):
        html = Path(file_path).read_text(encoding="utf8")
        base_url = QUrl.fromLocalFile(str(Path(file_path).absolute()))
        self.browser.setHtml(html, base_url)

    def execute_js(self, js_code):
        self.browser.page().runJavaScript(js_code)

def main():
    app = QApplication(sys.argv)
    window = HTMLWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()