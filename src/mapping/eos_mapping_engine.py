"""
Manages mapping of EOS data to internal states.
"""

from observer import Observer

class EOSMappingEngine(Observer):
    """
    Processes and maps EOS commands to internal states.

    Attributes:
    - state_manager: A reference to the central State Manager instance.
    """

    def __init__(self, logger, osc_client, state_manager=None):
        self._osc_client = osc_client
        self._state_manager = state_manager
        self.logger = logger

        self.eos_fader_bank_initilized = False



    def update(self, message):
        if message["type"] == "key_press":
            if message["key"] == "LIVE":
                self._osc_client.send_message(f"/eos/user/1/key/LIVE", message["value"])
            if message["key"] == "BLIND":
                self._osc_client.send_message(f"/eos/user/1/key/BLIND", message["value"])
        if message["type"] == "fader":
            self.init_eos_fader_bank()
            self._osc_client.send_message(f"/eos/user/1/fader/1/1", message["value"])
            self.logger.debug(f"Sending fader {message['id']} value {message['value']} to EOS")
            # Add logic for other keys as required

    def eos_osc_handler(self, unused_addr, *args):
        self.logger.info(f"EOS OSC Handler received: '{unused_addr}' {args}")
        if unused_addr == "/eos/out/cmd":
            self.logger.info("received cmd")
            if args[0].startswith("LIVE: "):
                self._state_manager.goLive()
            elif args[0].startswith("BLIND: "):
                self._state_manager.goBlind()

    def init_eos_fader_bank(self):
        """
        Initializes the EOS fader bank to receive fader messages.
        """
        if self.eos_fader_bank_initilized:
            return
        self._osc_client.send_message("/eos/user/1/fader/1/config/10",1)
        self.eos_fader_bank_initilized = True
        self.logger.info(f"EOS fader bank initialized with 10 faders.")