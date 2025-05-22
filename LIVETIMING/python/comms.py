import copy
import threading
import json
import logging
import time
from typing import Optional, Union
from websocket import create_connection, WebSocket, WebSocketException # type:ignore

class LivetimingHandler:
    """
    The way LivetimingHandler works is a little funny.
    I didn't want to delete/create a new one every time the connection was terminated,
    so I made it have 2 init functions.  What the `initialize` function does is close
    everything and reinitialize it, allowing for a new connection to start. 
    """
    def __init__(self):
        self._initialize()
        self.config_password = ""
        self.logger = logging.getLogger('BART2')

    def _initialize(self):
        """
        Explained above
        """
        from instances import Instances
        Instances.window.bridge.send_to_js(f"LIVETIMING|||t_started")
        self.primary_url = "wss://nyssra.pythonanywhere.com/livetiming-ws"
        self.websocket_connection: Optional[WebSocket] = None
        self.timeout_wait_sec = 20
        self.authenticated = False
        self.ping_interval = 15
        self.pong_wait_time = 20
        self.last_pong_time = time.time()  
        self.websocket_thread = None
        self.connection_ready = threading.Event()
        self.websocket_thread_running = False
        self.loop = None
        
    def reinit(self):
        """
        The real reinit function, this one is the one that cleans up everything
        """
        if self.websocket_thread_running:
            self._stop_websocket_thread()

        self._initialize()

    def connect_to_livetiming_ws(self, url: Union[str, None] = None):
        """
        If you can't figure out what this does, you shouldn't be looking at this code

        Args:
            url (Union[None, str], optional): The URL to connect to, this should almost always be None. Defaults to None.
        """
        if url is None:
            url = self.primary_url
        
        if not self.websocket_thread_running:
            self.websocket_thread_running = True
            self.websocket_thread = threading.Thread(target=self._connect_ws, args=(url,))
            self.websocket_thread.start()

    def _connect_ws(self, url: str):
        """
        Nothing crazy

        Args:
            url (str): The URL to connect to, inputted from `connect_to_livetiming_ws`.
        """
        try:
            self.websocket_connection = create_connection(url, timeout=self.timeout_wait_sec)
            self.logger.info(f"Successfully created WS connection to {url}")
            from instances import Instances
            Instances.window.bridge.send_to_js(f"LIVETIMING|||t_canceled")
            self.connection_ready.set() 
            self.start_ping_pong()

            self._listen_for_messages()

        except WebSocketException as e:
            self.logger.error(f"Livetiming WS error: {e}")
            self.reinit()
        except Exception as e:
            self.logger.error(f"Unexpected Livetiming WS error: {e}")
            self.reinit()
            
    def _listen_for_messages(self):
        """
        Just handles messages coming from the server
        """
        while self.websocket_thread_running:
            try:
                message = self.websocket_connection.recv()
                if message:
                    json_data = json.loads(message)
                    self.logger.debug(f"Received Livetiming WS message: {json_data}")

                    if "INFO_CLIENT_PONG" in json_data:
                        self.last_pong_time = time.time()

                    msg_type = json_data.get("type")
                    status = json_data.get("status")

                    if msg_type == "auth" and status == "success":
                        self.authenticated = True
                        self.logger.info("Authentication successful.")
                        from instances import Instances
                        if int(Instances.settings.get_setting("SAVE_PASSWORD")):
                            Instances.settings.update_setting("SAVED_PASSWORD", self.config_password)


                    elif msg_type == "auth" and status == "error":
                        self.logger.error(f"Authentication failed: {json_data.get('message')}")
                        self.reinit()
                        return

                    elif msg_type == "new_url" and status == "success":
                        self.logger.info(f"New route created: {json_data.get('new_route')}")

                    elif msg_type == "header" and status == "success":
                        self.logger.info("Header successfully written.")

                    elif msg_type == "data" and status == "success":
                        self.logger.debug("Livedata received and acknowledged.")

            except WebSocketException as e:
                self.logger.error(f"Livetiming WS receive error: {e}")
                self.reinit()
                break
            except Exception as e:
                self.logger.error(f"Unexpected Livetiming WS error: {e}")
                self.reinit()
                break

    def start_ping_pong(self):
        """
        Starts a ping/pong to the server to keep the connection alive.
        """
        def ping():
            while self.websocket_thread_running:
                current_time = time.time()

                if current_time - self.last_pong_time > self.pong_wait_time:
                    self.logger.error("No pong received in 20 seconds, shutting down Livetiming WS (Likely doesn't matter because if there is no ping, the server is dead).")
                    self.reinit()  
                    return

                
                ping_message = {"INFO_SERVER_PING": "ping"}
                self.websocket_connection.send(json.dumps(ping_message))
                self.logger.debug("Sent PING to server")

                time.sleep(self.ping_interval)  

        ping_thread = threading.Thread(target=ping)
        ping_thread.start()

    def _stop_websocket_thread(self):
        """
        Forcibly closes the connection and cleans up the Websocket thread.
        """
        self.websocket_thread_running = False
        if self.websocket_connection:
            try:
                self.websocket_connection.close()  
                self.connection_ready.clear()
                self.logger.info("Livetiming WS connection closed successfully.")
                self.reinit()
            except Exception as e:
                self.logger.error(f"Error closing Livetiming WS: {e}")
        if self.websocket_thread is not None:
            self.websocket_thread.join()

    def send_json_message(self, message: dict):
        """
        Sends a message to the server

        Args:
            message (dict): The message lol.
        """
        if self.websocket_connection:
            try:
                self.websocket_connection.send(json.dumps(message))
            except WebSocketException as e:
                self.logger.error(f"Error sending message to Livetiming WS: {e}")

    def send_auth_and_config(self, config: dict):
        """
        This function sends data to initialize a race and gets the Websocket ready to receive race results

        Args:
            config (dict): The config data, typically sent from the window and handled in `render.py`
        """
        if not self.connection_ready.wait(timeout=self.timeout_wait_sec):
            self.reinit()
            self.logger.error("WebSocket not ready in time for sending auth/config.")
            return

        self.logger.debug("WebSocket ready — sending auth/config")
        self.config_password = config['password']
        self.send_json_message({"password": config['password']})
        time.sleep(0.2)  
        self.send_json_message({'new_url': config['filename']})
        time.sleep(0.2)
        self.send_json_message(config['headers'])
        self.logger.debug(self.config_password)