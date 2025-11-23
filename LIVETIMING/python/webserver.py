import logging
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json

class LocalWebServer:
    """
    Hosts live results locally & easily.
    """
    def __init__(self):
        self.logger = logging.getLogger("BART2")
        self.results_data = {}
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        self.logger.info("Local web server started.")
    
    def update_results(self, results: dict) -> None:
        self.results_data = results
    
    def _run_server(self):
        os.chdir('webserver_static')
        server_address = ('', 8000)
        
        class LocalRequestHandler(SimpleHTTPRequestHandler):
            server_instance = self
            
            def do_GET(self):
                if self.path == "/results":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(LocalRequestHandler.server_instance.results_data).encode("utf-8")
                    )
                else:
                    super().do_GET()
        
        httpd = HTTPServer(server_address, LocalRequestHandler)
        self.logger.info("Serving HTTP on port 8000...")
        httpd.serve_forever()