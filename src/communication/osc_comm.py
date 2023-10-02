"""
Handles all OSC communications related to EOS.
Uses the python-osc library for communication.
"""

from pythonosc import udp_client
import unittest


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
        Sends a command to press the 'LIVE' key on EOS.
        """
        self.send_message("/eos/user/1/key/LIVE", 1)
        self.send_message("/eos/user/1/key/LIVE", 0)


class TestOSCClient(unittest.TestCase):

    def setUp(self):
        self.osc_client = OSCClient()

    def test_send_eos_live_key(self):
        # For this basic test, we're simply checking that no exceptions are raised
        # when sending the message.
        try:
            self.osc_client.send_eos_live_key()
            result = True
        except Exception as e:
            result = False
            print(f"Error encountered: {e}")

        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()