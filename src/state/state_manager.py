"""
Handles the central state of the system, acting as an intermediary between EOS and X-Touch mappings.
"""

from observer import Subject 

class StateManager(Subject):
    """
    Manages the internal state of the application and notifies observers of state changes.
    Extends the Subject class to provide observer pattern functionality.
    """

    def __init__(self):
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
        if id not in self.state['faders']:
            self.state['faders'][id]={}
        self.state['faders'][id]["name"] = name
        self.state['faders'][id]["color"] = "yellow"
        self.notify_observers({"type": "fadername", "id": id, "name": name, "color": self.state['faders'][id]["color"]})
