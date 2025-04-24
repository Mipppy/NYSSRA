import asyncio
import websockets
import logging
from typing import Optional

# Socketed the sockets on a websocket

"""
Livetiming rules!  nyssra.pythonanywhere.com/livetiming-ws
-----------------
**All messages MUST be valid JSON**

First message **must be** {"password": "***********"}
Second message **must be** {"new_url": "The file name of the race data. (Called new_url because I initially had a different idea on how to do this)"}
Third message are the headers for the race.  They must contain a {"name":"","place":""}, but any additional data about the race, such as hoster, etc, will be sent in here.
All following messages **must be** {"livedata": {RACE DATA}}, or they will be ignored by the server

"""

class ServerCommunications:
    
    def __init__(self) -> None:
        self.livetiming_websocket: Optional[websockets.WebSocketClientProtocol] = None  #type: ignore
        self.livetiming_loop: Optional[asyncio.AbstractEventLoop] = None
        self.primary_livetiming_url = "wss://nyssra.pythonanywhere.com/livetiming-ws"
        self.logging = logging.getLogger('BART2')
        self._connection_lock = asyncio.Lock()
        self._should_reconnect = False
        self._reconnect_attempts = 0
        self.max_reconnect_attempts = 3

    async def _livetiming_handler(self, livetiming_url: str = None) -> None:
        """Main WebSocket connection handler with reconnect support."""
        url = livetiming_url or self.primary_livetiming_url
        
        async with self._connection_lock:
            try:
                self.logging.info(f'Connecting to livetiming server: {url}')
                self.livetiming_websocket = await websockets.connect(url)
                self._reconnect_attempts = 0
                self.logging.info(f'Successfully connected to {url}')

                # Main message loop
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

    async def _attempt_reconnect(self, url: str) -> None:
        """Handle reconnection attempts with backoff."""
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
        """
        Open the WebSocket connection.
        
        Args:
            livetiming_url: Optional custom URL to connect to
            reconnect: Whether to automatically attempt reconnection if disconnected
        """
        if self.livetiming_loop and not self.livetiming_loop.is_closed():
            self.logging.warning("Connection already exists, closing first")
            self.close_livetiming()

        self._should_reconnect = reconnect
        self.livetiming_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.livetiming_loop)
        self.livetiming_loop.run_until_complete(self._livetiming_handler(livetiming_url))

    async def send_message(self, message: str) -> bool:
        """Safely send a message through the WebSocket."""
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

    def close_livetiming(self) -> None:
        """Close the WebSocket connection and clean up."""
        self._should_reconnect = False
        
        if self.livetiming_websocket and not self.livetiming_websocket.closed:
            self.livetiming_loop.run_until_complete(self.livetiming_websocket.close())
            self.livetiming_websocket = None
            self.logging.info("Closed WebSocket connection")

        if self.livetiming_loop and not self.livetiming_loop.is_closed():
            self.livetiming_loop.stop()
            self.livetiming_loop.close()
            self.livetiming_loop = None
            self.logging.debug("Closed event loop")
    
    def livetiming_send_password(self, password:str):
        None