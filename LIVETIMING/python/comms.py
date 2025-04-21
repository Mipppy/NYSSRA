import asyncio, websockets, logging

class ServerCommunications:
    """Static class for communicating with various servers, mainly the NYSSRA server, which is in /SITESERVER/""" 
    
    def __init__(self) -> None:
        self.livetiming_websocket = None
        self.livetiming_loop = None
        self.logging = logging.getLogger('BART2')

    async def _livetiming_handler(self, livetiming_url: str):
        try:
            async with websockets.connect(livetiming_url) as websocket:
                self.livetiming_websocket = websocket
                self.logging.info('Successfully created ')
                
                await websocket.send("Hello from client")

                async for message in websocket:
                    self.logging.debug(f"Received message '{message}' from {livetiming_url}")
        
        except websockets.exceptions.ConnectionClosed as e:
            self.logging.error(f"Websocket connection with {livetiming_url} closed with: {e}")
        except Exception as e:
            self.logging.error(f"Internal error while connecting to {livetiming_url}: {e}")

    def open_livetiming(self, livetiming_url: str) -> None:
        """Launch the WebSocket connection in a background thread with asyncio."""
        self.livetiming_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.livetiming_loop)
        self.livetiming_loop.run_until_complete(self._livetiming_handler(livetiming_url))
