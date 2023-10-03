"""
Manages mapping of X-Touch data to internal states.
"""

import os
from utils.json_handler import read_json

class XTouchMappingEngine:
    """
    Processes and maps X-Touch commands to internal states.

    Attributes:
    - state_manager: A reference to the central State Manager instance.
    - midi_map: Dictionary storing MIDI message to function mapping.
    """

    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.midi_map = self.load_midi_map()

    def load_midi_map(self):
        """
        Load the X-Touch MIDI mapping from a JSON file.

        Returns:
        - dict: A dictionary representing MIDI message to function mapping.
        """
        file_path = os.path.join("config", "xtouch_midi_map.json")
        filetree = read_json(file_path)

        # extract the mapping from the filetree
        # from type->coding->name to coding->(name,type)
        mapping = {}
        for type, codname in filetree.items():
            for coding, name in codname.items():
                mapping[coding] = (name, type)

        return mapping

    # Other methods related to X-Touch mapping will be defined here

    def map_midi_message(self, message):
        """
        Maps a MIDI message to a function/action using the midi_map.

        Parameters:
        - message: str, The MIDI message received.

        Returns:
        - str: The mapped function or action, or None if mapping does not exist.
        """
        id1Byte, *values = message.hex().split()
        id2Bytes = " ".join([id1Byte, values[0]])

        if id1Byte in self.midi_map:
            return (self.midi_map[id1Byte], " ".join(values))
        if id2Bytes in self.midi_map:
            return (self.midi_map[id2Bytes], " ".join(values[1::]))
        return None

    def handle_midi_message(self, message):
        """
        Handles an incoming MIDI message, utilizing the mappings.

        Parameters:
        - message: str, The MIDI message received.
        """

        action = self.map_midi_message(message)
        print(f"Action: {action}")
        if action:
            # Logic to handle mapped action goes here
            pass
        else:
            print(f"No mapped action for MIDI message: {message}")
