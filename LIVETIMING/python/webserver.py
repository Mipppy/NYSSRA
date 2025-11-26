from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import json
import socket
import os
import logging
from typing import List

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

    
    def update_results(self, results: List[dict]) -> None:
        self.results_data = results
        self.logger.info(self.results_data)
    
    def _run_server(self):
        web_dir = os.path.abspath("webserver_static")
        server_address = ('', 80)  
        parent_instance = self
        class LocalRequestHandler(SimpleHTTPRequestHandler):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=web_dir, **kwargs)

            def do_GET(self):
                if self.path == "/results":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(parent_instance.results_data).encode("utf-8")
                    )
                elif self.path == "/ip":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({
                            "local_ip": parent_instance.get_local_ip(),
                        }).encode("utf-8")
                    )
                else:
                    super().do_GET()
        
        httpd = HTTPServer(server_address, LocalRequestHandler)
        self.logger.info(f"Serving HTTP on port {server_address[1]}...")
        httpd.serve_forever()
        
    def get_local_ip(self):
        """Get the local IP address of the computer."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            from instances import Instances
            Instances.window.bridge.send_to_js(f"LOCAL_WEB_SERVER|||{local_ip}")
            return local_ip
        except Exception:
            return None
