import unittest
from src.communication.osc_comm import OSCClient

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
