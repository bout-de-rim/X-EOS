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
        if message["type"] == "fader" and message["origin"] != self:
            self.init_eos_fader_bank()
            self._osc_client.send_message(f"/eos/user/1/fader/1/{message['id']}", message["value"])
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
        elif unused_addr.startswith("/eos/fader/"):
            self.logger.debug(f"received fader message: {unused_addr.split('/')}={args[0]}")
            fader_id = int(unused_addr.split("/")[4])
            fader_value = args[0]
            self._state_manager.movingfader(fader_id, fader_value, self)

    def init_eos_fader_bank(self):
        """
        Initializes the EOS fader bank to receive fader messages.
        """
        if self.eos_fader_bank_initilized:
            return
        self._osc_client.send_message("/eos/user/1/fader/1/config/10",1)
        self.eos_fader_bank_initilized = True
        self.logger.info(f"EOS fader bank initialized with 10 faders.")