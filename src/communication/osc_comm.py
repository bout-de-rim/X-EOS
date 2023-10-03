"""
Handles all OSC communications related to EOS.
Uses the python-osc library for communication.
"""

from pythonosc import udp_client, dispatcher, osc_server
import socket

class OSCClient:
    """
    Establishes and manages an OSC client for communication with EOS.

    Attributes:
    - host: The hostname for OSC communication.
    - port: The port for OSC communication.
    """

    def __init__(self, host='127.0.0.1', port=8000):
        """
        Constructor for OSCClient.

        Args:
        - host: The hostname for OSC communication. Defaults to 'localhost'.
        - port: The port for OSC communication. Defaults to 8000.
        """
        self._client = udp_client.SimpleUDPClient(host, port)

    def dummy_callback(self, unused_addr, *args):
        """
        A dummy callback function for the OSC server.
        """
        print(f"OSC Server received: {args}")

    def start_server(self, root, callback=dummy_callback, initial_port=8003):
        """
        Starts an OSC server on the specified port.

        Args:
        - callback: The callback function to be called when a message is received.
        - port: The port to start the server on. Defaults to 8001.
        """
        self._dispatcher = dispatcher.Dispatcher()
        #self._dispatcher.map(root, callback)
        self._dispatcher.set_default_handler(callback)
        port = initial_port
        while True:
            try:
                self._server = osc_server.ThreadingOSCUDPServer(
                    ('127.0.0.1', port), self._dispatcher
                )
                print(f"OSC Server started at {self._server.server_address}")
                self._server.serve_forever()
                break  # Exit the loop if server starts successfully
            except (socket.error, OSError) as e:
                print(f"Port {port} is in use, trying {port + 1}...")
                port += 1  # Increment port and try again

    def send_message(self, address, value):
        """
        Sends an OSC message to the specified address with a given value.

        Args:
        - address: The OSC address pattern string.
        - value: The value to send.
        """
        self._client.send_message(address, value)

    def send_eos_live_key(self):
        """
        Sends a command to press and release the 'LIVE' key on EOS.
        """
        self.send_message("/eos/user/1/key/LIVE", 1)
        self.send_message("/eos/user/1/key/LIVE", 0)
