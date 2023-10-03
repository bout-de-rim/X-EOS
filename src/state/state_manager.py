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

    def key_pressed(self, key_name, value=1):
        """
        Update state based on key press and notify observers.

        Args:
        - key_name: The name of the key pressed.
        - value: The value associated with the key press (e.g., 1 for pressed).
        """
        self.state['keys'][key_name] = value
        self.notify_observers({"type": "key_press", "key": key_name, "value": value})

