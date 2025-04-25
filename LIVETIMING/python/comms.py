import asyncio
import websockets
import logging
from typing import Optional
import json
import threading

class ServerCommunications:
    
    def __init__(self) -> None:
        self.livetiming_websocket: Optional[websockets.WebSocketClientProtocol] = None  # type: ignore
        self.livetiming_loop: Optional[asyncio.AbstractEventLoop] = None
        self.primary_livetiming_url = "wss://nyssra.pythonanywhere.com/livetiming-ws"
        self.logging = logging.getLogger('BART2')
        self._connection_lock = asyncio.Lock()
        self._should_reconnect = False
        self._reconnect_attempts = 0
        self.max_reconnect_attempts = 3

    async def _livetiming_handler(self, livetiming_url: str = None) -> None:
        url = livetiming_url or self.primary_livetiming_url

        async with self._connection_lock:
            try:
                self.logging.info(f'Connecting to livetiming server: {url}')
                self.livetiming_websocket = await websockets.connect(url)
                self._reconnect_attempts = 0
                self.logging.info(f'Successfully connected to {url}')
                self.ping_task = asyncio.create_task(self._ping_loop())

                while True:
                    try:
                        message = await self.livetiming_websocket.recv()
                        self.logging.debug(f"Received message: {message}")
                        # Process message here
                    except websockets.exceptions.ConnectionClosed:
                        if not self._should_reconnect:
                            break
                        await self._attempt_reconnect(url)
                        continue
            except Exception as e:
                self.logging.error(f"Connection error: {e}")
                await self.close_livetiming()
                if self._should_reconnect:
                    await self._attempt_reconnect(url)

    async def _ping_loop(self) -> None:
        while self.livetiming_websocket and not self.livetiming_websocket.closed:
            try:
                await self.livetiming_websocket.send(json.dumps({"INFO_CLIENT_PING": "still alive"}))
                self.logging.debug("Sent keep-alive ping")
            except Exception as e:
                self.logging.warning(f"Ping failed: {e}")
                break
            await asyncio.sleep(2)

    async def _attempt_reconnect(self, url: str) -> None:
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            self.logging.error("Max reconnection attempts reached")
            self._should_reconnect = False
            return

        self._reconnect_attempts += 1
        backoff_time = min(5 * self._reconnect_attempts, 30)
        self.logging.info(f"Attempting reconnect #{self._reconnect_attempts} in {backoff_time}s...")
        await asyncio.sleep(backoff_time)
        await self._livetiming_handler(url)

    def open_livetiming(self, livetiming_url: str = None, reconnect: bool = True) -> None:
        def start_loop():
            self._should_reconnect = reconnect
            self.livetiming_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.livetiming_loop)
            self.livetiming_loop.run_until_complete(self._livetiming_handler(livetiming_url))

        threading.Thread(target=start_loop, daemon=True).start()

    async def send_message(self, message: str) -> bool:
        try:
            if not self.livetiming_websocket or self.livetiming_websocket.closed:
                self.logging.warning("Cannot send message - not connected")
                return False

            await self.livetiming_websocket.send(message)
            self.logging.debug(f"Sent message: {message}")
            return True

        except Exception as e:
            self.logging.error(f"Failed to send message: {e}")
            return False

    async def _send_auth_and_config(self, information: dict) -> None:
        while not self.livetiming_websocket or self.livetiming_websocket.closed:
            await asyncio.sleep(0.2)

        await self.send_message(json.dumps({"password": information['password']}))
        await self.send_message(json.dumps({"new_url": information['filename']}))
        await self.send_message(json.dumps(information['headers']))

    def livetiming_send_auth_and_config(self, information: dict) -> None:
        self.open_livetiming()

        if self.livetiming_loop and not self.livetiming_loop.is_closed():
            self.livetiming_loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._send_auth_and_config(information))
            )
        else:
            self.logging.error("Cannot send messages — Event loop is not running")

    def close_livetiming(self) -> None:
        self._should_reconnect = False

        if self.livetiming_websocket and not self.livetiming_websocket.closed:
            self.livetiming_loop.run_until_complete(self.livetiming_websocket.close())
            self.livetiming_websocket = None
            if hasattr(self, "ping_task") and self.ping_task:
                try:
                    self.ping_task.cancel()
                except Exception as e:
                    self.logging.warning(f"Failed to cancel ping task: {e}")
            self.logging.info("Closed WebSocket connection")

        if self.livetiming_loop and not self.livetiming_loop.is_closed():
            self.livetiming_loop.stop()
            self.livetiming_loop.close()
            if hasattr(self, "ping_task") and self.ping_task:
                try:
                    self.ping_task.cancel()
                except Exception as e:
                    self.logging.warning(f"Failed to cancel ping task: {e}")

            self.livetiming_loop = None
            self.logging.debug("Closed event loop")
