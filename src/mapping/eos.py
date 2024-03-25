

class EOS: 
    def __init__(self, osc_client, logger):
        self._osc_client = osc_client
        self.logger = logger
        self.user = 1
        self.faderBank = EOSFaderBank(self, 10)
        self.faderBank.init_on_eos()

    def pressKey(self, key_name, hold=False):
        self.send(f"key/{key_name}", 1)
        if not hold:
            self.releaseKey(key_name)
    
    def releaseKey(self, key_name):
        self.send(f"key/{key_name}", 0)

    

    def eos_osc_handler(self, unused_addr, *arg):
        self.logger.debug(f"OSC message: {unused_addr}={arg}")
        segmented = unused_addr.split("/")
        if segmented[2] == "fader": 
            self.faderBank.faders[int(segmented[3])].setValue(arg[0])
        elif segmented[2] == "out":
            pass
        else:
            self.logger.warning(f"Unknown OSC message from EOS: {unused_addr}={arg}")

    def send(self, url, value):
        self._osc_client.send_message(f"/eos/user/{self.user}/{url}", value)


class EOSFader:
    def __init__(self, id, faderBank):
        self.faderBank = faderBank
        self.id = id
        self.type = None # Sub, Global FX, Inibit, etc.
        self.value = 0.0

    def setValue(self, value):
        if value == self.value:
            return
        self.value = value
        self.faderBank.send(f"{self.id}", value)

    def setName(self, name):
        if name == self.name:
            return
        self.name = name
        #"/eos/user/{UID}/fader/{FBankId}/{self.id}"
        self.faderBank.send(f"{self.id}/name", name)

    def __str__(self):
        return f"Fader {self.id} ({self.name}) from {self.faderBank}"

    def __repr__(self):
        return f"Fader {self.id} ({self.name}) from {self.faderBank}"
    

class EOSFaderBank:
    def __init__(self, eos, width,):
        self.eos = eos
        self.width = width
        self.active_page = 0
        self.eos_osc_id = 1
        self.faders = [EOSFader(i, self) for i in range(1, width + 1)]
        self.initialized = False

    def init_on_eos(self):
        if self.initialized:
            return
        #"/eos/user/{UID}/fader/{FBankId}/{self.id}/"
        self.send(f"config/{self.width}")
        self.initialized = True

    def pageNext(self):
        self.active_page = min(self.active_page + 1, 8)
        self.setPage(self.active_page)

    def pagePrev(self): 
        self.active_page = max(self.active_page - 1, 1)
        self.setPage(self.active_page)

    def setPage(self, page):
        #model: /eos/user/1/fader/3/config/2/10
        if self.eos_osc_id is None: 
            raise AssertionError("EOS OSC ID is not set")
        #"/eos/user/{UID}/fader/{FBankId}/{self.id}/"
        self.send(f"config/{self.active_page}/{self.width}")

    def send(self, url, value=None):
        #"/eos/user/{self.user}/.."
        self.eos.send(f"fader/{self.eos_osc_id}/{url}", value)

    def __str__(self):
        return f"Fader bank {self.eos_osc_id} with {self.width} faders"