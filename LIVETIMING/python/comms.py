import threading
import json
import logging
import time
from typing import Optional, Union
from websocket import create_connection, WebSocket, WebSocketException

class LivetimingHandler:
    def __init__(self):
        self._initialize()
        self.websocket_thread = None
        self.connection_ready = threading.Event()
        self.websocket_thread_running = False
        self.loop = None
        self.logger = logging.getLogger('BART2')

    def _initialize(self):
        self.primary_url = "wss://nyssra.pythonanywhere.com/livetiming-ws"
        self.websocket_connection: Optional[WebSocket] = None
        self.timeout_wait_sec = 20
        self.authenticated = False
        self.ping_interval = 15
        self.pong_wait_time = 20
        self.last_pong_time = time.time()  

    def reinit(self):
        if self.websocket_thread_running:
            self._stop_websocket_thread()

        self._initialize()

    def connect_to_livetiming_ws(self, url: Union[None, str] = None):
        if url is None:
            url = self.primary_url
        
        if not self.websocket_thread_running:
            self.websocket_thread_running = True
            self.websocket_thread = threading.Thread(target=self._connect_ws, args=(url,))
            self.websocket_thread.start()

    def _connect_ws(self, url: str):
        try:
            self.websocket_connection = create_connection(url, timeout=self.timeout_wait_sec)
            self.logger.info(f"Successfully created WS connection to {url}")
            self.connection_ready.set() 
            self.start_ping_pong()

            self._listen_for_messages()

        except WebSocketException as e:
            self.logger.error(f"Livetiming WS error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected Livetiming WS error: {e}")

    def _listen_for_messages(self):
        while self.websocket_thread_running:
            try:
                message = self.websocket_connection.recv()
                if message:
                    json_data = json.loads(message)
                    self.logger.debug(f"Received Livetiming WS message: {json_data}")

                    if "INFO_CLIENT_PONG" in json_data:
                        self.last_pong_time = time.time()  
                        self.logger.debug("Received PONG from server")

            except WebSocketException as e:
                self.logger.error(f"Livetiming WS receive error: {e}")
                break
            except Exception as e:
                self.logger.error(f"Unexpected Livetiming WS error: {e}")
                break

    def start_ping_pong(self):
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
        self.websocket_thread_running = False
        if self.websocket_connection:
            try:
                self.websocket_connection.close()  
                self.connection_ready.clear()
                self.logger.info("Livetiming WS connection closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing Livetiming WS: {e}")
        if self.websocket_thread is not None:
            self.websocket_thread.join()

    def send_json_message(self, message: dict):
        if self.websocket_connection:
            try:
                self.websocket_connection.send(json.dumps(message))
            except WebSocketException as e:
                self.logger.error(f"Error sending message to Livetiming WS: {e}")

    def send_auth_and_config(self, config: dict):
        # FIXME: Headers not being in config
        if not self.connection_ready.wait(timeout=5):
            self.logger.error("WebSocket not ready in time for sending auth/config.")
            return

        self.logger.debug("WebSocket ready — sending auth/config")

        self.send_json_message({"password": config['password']})
        time.sleep(0.2)  
        self.send_json_message({'new_url': config['filename']})
        time.sleep(0.2)
        self.send_json_message(config['headers'])




# class ServerCommunications:

#     def __init__(self) -> None:
#         self.livetiming_websocket: Optional[websockets.WebSocketClientProtocol] = None  # type: ignore
#         self.livetiming_loop: Optional[asyncio.AbstractEventLoop] = None
#         self.primary_livetiming_url = "wss://nyssra.pythonanywhere.com/livetiming-ws"
#         self.logging = logging.getLogger('BART2')
#         self._connection_lock = asyncio.Lock()
#         self._should_reconnect = False
#         self._reconnect_attempts = 0
#         self.max_reconnect_attempts = 3

#     async def _livetiming_handler(self, livetiming_url: str = None) -> None:
#         url = livetiming_url or self.primary_livetiming_url

#         async with self._connection_lock:
#             try:
#                 self.logging.info(f'Connecting to livetiming server: {url}')
#                 self.livetiming_websocket = await websockets.connect(url)
#                 self._reconnect_attempts = 0
#                 self.logging.info(f'Successfully connected to {url}')
#                 self.ping_task = asyncio.create_task(self._ping_loop())

#                 while True:
#                     try:
#                         message = await self.livetiming_websocket.recv()
#                         self.logging.info(f"Received message: {message}")
#                         # Process message here
#                     except websockets.exceptions.ConnectionClosed:
#                         if not self._should_reconnect:
#                             break
#                         await self._attempt_reconnect(url)
#                         continue
#             except Exception as e:
#                 self.logging.error(f"Connection error: {e}")
#                 await self.close_livetiming()
#                 if self._should_reconnect:
#                     await self._attempt_reconnect(url)

#     async def _ping_loop(self) -> None:
#         while self.livetiming_websocket and not getattr(self.livetiming_websocket, 'closed', True):
#             try:
#                 await self.send_message(json.dumps({"INFO_CLIENT_PING": "still alive"}))
#                 self.logging.debug("Sent keep-alive ping")
#             except Exception as e:
#                 self.logging.warning(f"Ping failed: {e}")
#                 break
#             await asyncio.sleep(2)

#     async def _attempt_reconnect(self, url: str) -> None:
#         if self._reconnect_attempts >= self.max_reconnect_attempts:
#             self.logging.error("Max reconnection attempts reached")
#             self._should_reconnect = False
#             return

#         self._reconnect_attempts += 1
#         backoff_time = min(5 * self._reconnect_attempts, 30)
#         self.logging.info(f"Attempting reconnect #{self._reconnect_attempts} in {backoff_time}s...")
#         await asyncio.sleep(backoff_time)
#         await self._livetiming_handler(url)

#     def open_livetiming(self, livetiming_url: str = None, reconnect: bool = True) -> None:
#         def start_loop():
#             self._should_reconnect = reconnect
#             self.livetiming_loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(self.livetiming_loop)
#             self.livetiming_loop.run_until_complete(self._livetiming_handler(livetiming_url))

#         threading.Thread(target=start_loop, daemon=True).start()

#     async def send_message(self, message: str) -> bool:
#         try:
#             if not self.livetiming_websocket or getattr(self.livetiming_websocket, 'closed', True):
#                 self.logging.warning("Cannot send message - not connected")
#                 return False

#             await self.livetiming_websocket.send(message)
#             self.logging.info(f"Sent message: {message}")
#             return True

#         except Exception as e:
#             self.logging.error(f"Failed to send message: {e}")
#             return False

#     async def _send_auth_and_config(self, information: dict) -> None:
#         while not self.livetiming_websocket or getattr(self.livetiming_websocket, 'closed', True):
#             await asyncio.sleep(0.2)

#         await self.send_message(json.dumps({"password": information['password']}))
#         await self.send_message(json.dumps({"new_url": information['filename']}))
#         await self.send_message(json.dumps(information['headers']))

#     def livetiming_send_auth_and_config(self, information: dict) -> None:
#         self.open_livetiming(self.primary_livetiming_url, True)

#         def schedule_auth_and_config():
#             asyncio.create_task(self._send_auth_and_config(information))

#         if self.livetiming_loop and not self.livetiming_loop.is_closed():
#             self.livetiming_loop.call_soon_threadsafe(schedule_auth_and_config)
#         else:
#             self.logging.error("Cannot send messages — Event loop is not running")

#     def close_livetiming(self) -> None:
#         self._should_reconnect = False

#         if self.livetiming_websocket and not getattr(self.livetiming_websocket, 'closed', True):
#             self.livetiming_loop.run_until_complete(self.livetiming_websocket.close())
#             self.livetiming_websocket = None
#             if hasattr(self, "ping_task") and self.ping_task:
#                 try:
#                     self.ping_task.cancel()
#                 except Exception as e:
#                     self.logging.warning(f"Failed to cancel ping task: {e}")
#             self.logging.info("Closed WebSocket connection")

#         if self.livetiming_loop and not self.livetiming_loop.is_closed():
#             self.livetiming_loop.stop()
#             self.livetiming_loop.close()
#             if hasattr(self, "ping_task") and self.ping_task:
#                 try:
#                     self.ping_task.cancel()
#                 except Exception as e:
#                     self.logging.warning(f"Failed to cancel ping task: {e}")
#             self.livetiming_loop = None
#             self.logging.debug("Closed event loop")
