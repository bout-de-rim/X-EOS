"""
Handles the central state of the system, acting as an intermediary between EOS and X-Touch mappings.
"""

from observer import Subject 

class StateManager(Subject):
    """
    Manages the internal state of the application and notifies observers of state changes.
    Extends the Subject class to provide observer pattern functionality.
    """

    def __init__(self, logger=None):
        """
        Initializes the StateManager with default or initial state values.
        """
        super().__init__()  # Call the base class's constructor
        self.state = {
            'faders': {},
            'encoders': {},
            'keys': {},
            # ... any other initial state items based on EOS semantics
        }
        # the EOS programmer state LIVE, BLIND, STAGINGMODE, unknown
        self.programmer_state = "unknown"
        
        self.eos = None
        self.xtouch = None
        self.logger = logger


    def key_pressed(self, key_name, value=1):
        """
        Update state based on key press and notify observers.

        Args:
        - key_name: The name of the key pressed.
        - value: The value associated with the key press (e.g., 1 for pressed).
        """
        #print("key pressed: ", key_name, value)
        self.state['keys'][key_name] = value
        self.notify_observers({"type": "key_press", "key": key_name, "value": value})

    def goLive(self):
        """
        Update state based on key press and notify observers.
        """
        if self.programmer_state == "LIVE":
            return
        self.programmer_state = "LIVE"
        self.notify_observers({"type": "goLive"})

    def goBlind(self):
        """
        Update state based on key press and notify observers.
        """
        if self.programmer_state == "BLIND":
            return
        self.programmer_state = "BLIND"
        self.notify_observers({"type": "goBlind"})

    def movingfader(self,id,value,origin): 
        if id not in self.state['faders']:
            self.state['faders'][id]={}
            self.state['faders'][id]["value"] = value
        elif int(1000*self.state['faders'][id]["value"]) == int(1000*value):
            return
        self.state['faders'][id]["value"] = value
        self.notify_observers({"type": "fader", "id": id, "value": value, "origin": origin})

    def namingfader(self,id,name): 
        #if id not in self.state['faders']:
        #    self.state['faders'][id]={}
        #self.state['faders'][id]["name"] = name
        #self.state['faders'][id]["color"] = "yellow"

        # fader out of range of the X-Touch
        if id not in range(1,9):
            return
        
        split_name = name.split(" ")
        target_type = split_name[0]
        target_id = split_name[1] if len(split_name) > 1 else ""
        target_name = " ".join(split_name[2:]) if len(split_name) > 2 else ""       

        # eos fader targets: CL, S, IP, FP, CP, BP, PR, GM, Man Time, Gobal FX, unmapped
        self.xtouch.setScribbleText(0, id-1, f"{target_type} {target_id}"[:7])
        self.xtouch.setScribbleText(1, id-1, target_name[:7])
        # colors: ["off", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        faderColor = {"CL": "green", "S": "yellow", "IP":"yellow", "FP":"green", "CP":"white", "BP":"blue", "Pr":"cyan", "GM":"red", "Man":"green", "Global":"magenta", "":"off"}
        
        self.xtouch.setScribbleColor(id-1, faderColor[target_type] if target_type in faderColor else "white")

    def faderPageChanged(self,page):
        #self.logger.debug(f"Page changed to {page}")
        for i in range(1,9): 
           self.xtouch.setButtonLed(f"Rec/Rdy {i}", "On" if i==page else "Off")

    def setFaderPage(self,page):
        self.eos.eos_fader_bank.setPage(page)

    def cue_playing(self, cueId, cueText, cueTime): 
        self.xtouch.set7segment(cueId+" "+cueTime)
