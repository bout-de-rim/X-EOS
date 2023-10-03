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
    - midi_id_map: Dictionary mapping MCU identifiers to (id_name, element_type).
    - midi_value_map: Dictionary mapping element_type to {hexvalue: value}.
    """

    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.midi_id_map, self.midi_value_map = self.load_midi2mcu_map()
        self.mcu2semantic_map = self.load_mcu2semantic_map()

    def load_midi2mcu_map(self):
        """
        Load the X-Touch MIDI mapping from a JSON file.

        Returns:
        - dict: A dictionary representing MIDI message to function mapping.
        """
        file_path = os.path.join("config", "xtouch_midi_map.json")
        filetree = read_json(file_path)

        # extract the mapping from the filetree
        # from type->coding->name to coding->(name,type)
        idmapping = {}
        valuespace={}
        for type, codname in filetree.items():
            for coding, name in codname.items():
                if coding == "values": 
                    valuespace[type] = name
                else:
                    idmapping[coding] = (name, type)

        return (idmapping, valuespace)

    def load_mcu2semantic_map(self):
        """
        Load the X-Touch MCU mapping from a JSON file.
        xtouch_cmds.json contains the mapping from MCU to commands.
        Only pairs like "Rec/Rdy 1": "EOS_MACRO_1". 
        
        Returns:
        - dict: A dictionary representing MCU message to function mapping.
        """
        file_path = os.path.join("config", "xtouch_cmds.json")
        return read_json(file_path)

        

    def map_midi2mcu(self, message):
        """
        Maps a MIDI message to MCU element identifiers using midi_id_map.

        Parameters:
        - message: mido Message, The MIDI message received.

        Returns:
        - tuple: (type, id, value) if the message is mapped, None otherwise.
        """
        id1Byte, *values = message.hex().split()
        id2Bytes = " ".join([id1Byte, values[0]])

        if id1Byte in self.midi_id_map:
            (id,type), hexvalue = (self.midi_id_map[id1Byte], " ".join(values))
        elif id2Bytes in self.midi_id_map:
            (id,type), hexvalue = (self.midi_id_map[id2Bytes], " ".join(values[1::]))
        else:
            print(f"No mapped MCU for MIDI message: {message}")
            return None
        if type in self.midi_value_map:
            value = self.midi_value_map[type].get(hexvalue, None)
        else:
            print(self.midi_value_map)
            value = hexvalue
        return (type, id, value)


    def handle_midi_message(self, message):
        """
        Handles an incoming MIDI message, utilizing the mappings.

        Parameters:
        - message: str, The MIDI message received.
        """
        try:
            (type, id, value) = self.map_midi2mcu(message)

            if id in self.mcu2semantic_map and self.mcu2semantic_map[id] != "":
                if type == "switch":
                    if value == "Pressed":
                        self.state_manager.key_pressed(self.mcu2semantic_map[id])
                    elif value == "Released":
                        self.state_manager.key_pressed(self.mcu2semantic_map[id], 0)
            else:
                print(f"No mapped action for {type} '{id}' '{value}'")
        except ValueError as e:
            print(e)
