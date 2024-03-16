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

        self.eos_fader_bank = EOSFaderBank(osc_client, 10)



    def update(self, message):
        if message["type"] == "key_press":
            if message["key"].startswith("EOS_"):
                self._osc_client.send_message(f"/eos/user/1/key/{message['key'][4:]}", message["value"])
            elif message["key"] == "FADER_PAGE_NEXT":
                self.eos_fader_bank.pageNext()
            elif message["key"] == "FADER_PAGE_PREV":
                self.eos_fader_bank.pagePrev()
        elif message["type"] == "fader" and message["origin"] != self:
            self.eos_fader_bank.init_on_eos()
            self.eos_fader_bank.faders[int(message["id"])-1].setValue(message["value"])

    def eos_osc_handler(self, unused_addr, *args):
        #self.logger.info(f"EOS OSC Handler received: '{unused_addr}' {args}")
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
        elif unused_addr.startswith("/eos/out/fader/"):
            cmd=unused_addr.split('/')
            if len(cmd) >=7 and cmd[6]=="name": 
                self.logger.debug(f"received fader name: {cmd[4]}={args[0]}")
                self._state_manager.namingfader(int(cmd[4]),args[0])
                self.eos_fader_bank.faders[int(cmd[4])-1].name = args[0]
                #self._state_manager.notify_observers({"type": "eosfadername", "id": int(cmd[4]), "name": args[0]})
                self._state_manager.namingfader(int(cmd[4]),args[0])
            elif cmd[4]=="range":
                pass
            elif cmd[4]==self.eos_fader_bank.eos_osc_id and len(cmd) == 5:
                # String argument with descriptive text for the OSC fader bank at <index>
                pass
            else:
                self.logger.info(f"received unknown fader message: {cmd}={args}")
        
class EOSFader:
    def __init__(self, osc_client, id, name):
        self._osc_client = osc_client
        self.id = id
        self.name = name
        self.type = None # Sub, Global FX, Inibit, etc.
        self.value = 0.0

    def setValue(self, value):
        if value == self.value:
            return
        self.value = value
        self._osc_client.send_message(f"/eos/user/1/fader/1/{self.id}", value)

    def setName(self, name):
        if name == self.name:
            return
        self.name = name
        self._osc_client.send_message(f"/eos/user/1/fader/1/{self.id}/name", name)

    def __str__(self):
        return f"Fader {self.id} ({self.name})"

    def __repr__(self):
        return f"Fader {self.id} ({self.name})"
    
class EOSFaderBank:
    def __init__(self, osc_client, width):
        self._osc_client = osc_client
        self.width = width
        self.active_page = 0
        self.eos_osc_id = 1
        self.faders = [EOSFader(osc_client, i, f"Fader {i}") for i in range(1, width + 1)]
        self.initialized = False

    def init_on_eos(self):
        if self.initialized:
            return
        self.eos_osc_id = self._osc_client.send_message(f"/eos/user/1/fader/{self.eos_osc_id}/config/{self.width}", 1)
        self.initialized = True

    def pageNext(self):
        self.active_page = min(self.active_page + 1, 10)
        self.setPage(self.active_page)

    def pagePrev(self): 
        self.active_page = max(self.active_page - 1, 1)
        self.setPage(self.active_page)

    def setPage(self, page):
        #model: /eos/user/1/fader/3/config/2/10
        self._osc_client.send_message(f"/eos/user/1/fader/{self.eos_osc_id}/config/{self.active_page}/{self.width}", 1)
        print(f"Fader page {self.active_page}")

    def __str__(self):
        return f"EOS OSC Fader Bank {self.eos_osc_id} (Current page {self.active_page}): {self.faders}"

    def __repr__(self):
        return f"EOS OSC Fader Bank {self.eos_osc_id} (Current page {self.active_page}): {self.faders}"