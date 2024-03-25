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

        self.eos_fader_bank = EOSFaderBank(osc_client, 10, state_manager)

    def update(self, message):
        if message["type"] == "key_press":
            if message["key"].startswith("EOS_"):
                self.logger.info(f"Received EOS key press: {message}")
                self._osc_client.send_message(f"/eos/user/1/key/{message['key'][4:]}", message["value"])
                return
            if message["key"] == "FADER_PAGE_NEXT" and message["value"] == 0:
                self.eos_fader_bank.pageNext()
                return
            if message["key"] == "FADER_PAGE_PREV" and message["value"] == 0:
                self.eos_fader_bank.pagePrev()
                return
            if message["key"].startswith("FADER_PAGE_") and message["value"] == 0:
                self.eos_fader_bank.setPage(int(message["key"][-1:]))
                return
            if message["key"].startswith("FADERB"):
                type, id, action = message["key"].split("_")
                try: 
                    actions = {"FIRE": self.eos_fader_bank.get(int(id)).fire, "STOP": self.eos_fader_bank.get(int(id)).stop, "LOAD": self.eos_fader_bank.get(int(id)).load}
                except Exception as e:
                    self.logger.error(f"Error processing fader action: {e}")
                    return
                actions[action](message["value"])
                return
            self.logger.info(f"Unknown key press: {message}")
            return

    def eos_osc_handler(self, unused_addr, *args):
        #self.logger.info(f"EOS OSC Handler received: '{unused_addr}' {args}")
        if unused_addr == "/eos/out/cmd":
            self.logger.info("received cmd")
            if args[0].startswith("LIVE: "):
                self._state_manager.goLive()
            elif args[0].startswith("BLIND: "):
                self._state_manager.goBlind()
        elif unused_addr.startswith("/eos/fader/"):
            #self.logger.debug(f"received fader message: {unused_addr.split('/')}={args[0]}")
            fader_id = int(unused_addr.split("/")[4])
            fader = self.eos_fader_bank.faders[fader_id - 1]
            # Avoid rounding loops between EOS and the X-Touch
            if abs(args[0] - fader.value) > 1/255.0:
                fader.value=args[0]
                self._state_manager.eosMovesFader(fader)
        elif unused_addr.startswith("/eos/out/fader/"):
            cmd=unused_addr.split('/')
            if len(cmd) >=7 and cmd[6]=="name": 
                #self.logger.debug(f"received fader name: {cmd}={args[0]}")
                self._state_manager.namingfader(int(cmd[5]),args[0])
                self.eos_fader_bank.faders[int(cmd[4])-1].name = args[0]
                #self._state_manager.notify_observers({"type": "eosfadername", "id": int(cmd[4]), "name": args[0]})
                self._state_manager.namingfader(int(cmd[5]),args[0])
            elif cmd[4]=="range":
                pass
            elif cmd[4]==str(self.eos_fader_bank.eos_osc_id) and len(cmd) == 5:
                # String argument with descriptive text for the OSC fader bank at <index>
                self._state_manager.faderPageChanged(int(args[0]))
            else:
                self.logger.info(f"received unknown fader message ({len(cmd)}): {cmd}={args}")
        elif unused_addr.startswith("/eos/out/active/cue/text"):
            self.logger.debug(f"received active cue: {args[0]}")
            self.logger.debug(f"received remaining time: {args[0].split(' ')[-2]}")
            text_arr = args[0].split(' ')
            self._state_manager.cue_playing(text_arr[0], ' '.join(text_arr[1:-2]), text_arr[-2])
        
class EOSFader:
    def __init__(self, osc_client, bank, id, name):
        self._osc_client = osc_client
        self.id = id
        self.name = name
        self.type = None # Sub, Global FX, Inibit, etc.
        self.value = 0.0
        self.bank = bank
        self.fired = False

    def fire(self, value):
        self.fired = value
        self._action("fire", value)

    def stop(self, value):
        self._action("stop", value)

    def load(self, fader_id, value):
        self._action("load", value)

    def _action(self, action, value):
        #/eos/user/1/fader/1/10/fire
        self._osc_client.send_message(f"/eos/user/1/fader/{self.bank.eos_osc_id}/{self.id}/{action}", value)

    def setValue(self, value):
        # Avoid rounding loops between EOS and the X-Touch
        if abs(value - self.value) < 1/255.0:
            return
        self.value = value
        self.sync_value()

    def sync_value(self):    
        self._osc_client.send_message(f"/eos/user/1/fader/1/{self.id}", self.value)

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
    def __init__(self, osc_client, width, state_manager):
        self._osc_client = osc_client
        self.width = width
        self.active_page = 0
        self.eos_osc_id = 1
        self.faders = [EOSFader(osc_client, self, i, f"Fader {i}") for i in range(1, width + 1)]
        self.initialized = False
        self.state_manager = state_manager

    def get(self, fader_id):
        return self.faders[fader_id - 1]

    def init_on_eos(self):
        if self.initialized:
            return
        self._osc_client.send_message(f"/eos/user/1/fader/{self.eos_osc_id}/config/{self.width}", 1)
        self.initialized = True

    def pageNext(self):
        self.setPage(min(self.active_page + 1, 8))

    def pagePrev(self): 
        self.setPage(max(self.active_page - 1, 1))

    def setPage(self, page):
        #model: /eos/user/1/fader/3/config/2/10
        if self.eos_osc_id is None: 
            raise AssertionError("EOS OSC ID is not set")
        self.active_page = page
        self._osc_client.send_message(f"/eos/user/1/fader/{self.eos_osc_id}/config/{self.active_page}/{self.width}", 1)
        #self.state_manager.faderPageChanged(page)
        self.state_manager.logger.debug(f"Fader page {self.active_page}")

    def __str__(self):
        return f"EOS OSC Fader Bank {self.eos_osc_id} (Current page {self.active_page}): {self.faders}"

    def __repr__(self):
        return f"EOS OSC Fader Bank {self.eos_osc_id} (Current page {self.active_page}): {self.faders}"