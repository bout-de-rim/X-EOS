"""
Manages mapping of X-Touch data to internal states.
"""

import os
from utils.json_handler import read_json
from observer import Observer

class XTouchMappingEngine(Observer):
    """
    Processes and maps X-Touch commands to internal states.

    Attributes:
    - state_manager: A reference to the central State Manager instance.
    - midi_id_map: Dictionary mapping MCU identifiers to (id_name, element_type).
    - midi_value_map: Dictionary mapping element_type to {hexvalue: value}.
    """

    def __init__(self, logger, state_manager):
        self.state_manager = state_manager
        self.midi_id_map, self.midi_value_map = self.load_midi2mcu_map()
        self.mcu2midi = self.load_mcu2midi_map()
        self.mcu2semantic_map = self.load_mcu2semantic_map()
        self._midi_comm = None
        self.logger = logger

    def update(self, message):
        if message["type"] == "goLive":
            self.logger.debug("sending goLive to X-Touch")
            self._midi_comm.send_midi_hex("90 3E 7F")
            self._midi_comm.send_midi_hex("90 3F 00")
        elif message["type"] == "goBlind":
            self.logger.debug("sending goBlind to X-Touch")
            self._midi_comm.send_midi_hex("90 3E 00")
            self._midi_comm.send_midi_hex("90 3F 7F")
        elif message["type"] == "fader":
            #self.logger.debug(message)
            if (message["origin"]!=self): 
                self.movefader(message["id"],message["value"])

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
    
    def load_mcu2midi_map(self):
        """
        Load the X-Touch MCU mapping from a JSON file.
        xtouch_midi_map.json contains the mapping MIDI -> MCU, arranged by type of control element. 
        Ex : {"fader": {"1": "E0"}}
        Returns:
        - dict: {"type": {"MCU": "MIDI"}}} for example dict["fader"]["1"]=="E0".
        """
        file_path = os.path.join("config", "xtouch_midi_map.json")
        filetree = read_json(file_path)
        mapping = {}
        for type, midi2mcu in filetree.items():
            mapping[type] = {}
            for midi, mcu in midi2mcu.items():
                if isinstance(mcu, dict):
                    # Handle the case where mcu is a dictionary
                    for key, value in mcu.items():
                        mapping[type][key] = value
                else:
                    mapping[type][mcu] = midi
        return mapping


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
    
    def movefader(self, id, value): 
        try:
            self._midi_comm.send_midi_hex(self.mcu2midi["fader"][str(id)]+" "+self.floatTo14bits(value))
        except KeyError as e:
            self.logger.warning(f"MCU fader {id} not found in mapping ({self.mcu2midi['fader'].keys()})")

        

    def map_midi2mcu(self, message):
        """
        Maps a MIDI message to MCU (Mackie Control Universal) element identifiers using midi_id_map.
        
        This function converts incoming MIDI messages into a format that identifies the type of control element
        (e.g., fader, knob, button), its identifier, and the value associated with the action on the control surface.
        
        Parameters:
        - message: mido.Message. The MIDI message received.
        
        Returns:
        - tuple: (type, id, value) if the message is mapped, None otherwise.
        'type' is the type of the MCU element (e.g., fader, button),
        'id' is the identifier of the element, and
        'value' is the value associated with the action (e.g., fader position, button press).
        """
        
        # Split the MIDI message into its hexadecimal components
        id1Byte, *values = message.hex().split()
        # Combine the first two bytes for cases where the identification requires two bytes
        id2Bytes = " ".join([id1Byte, values[0]])

        # First, try to match the message using the first byte (id1Byte)
        if id1Byte in self.midi_id_map:
            # If found, extract the (id, type) tuple and remaining values as hexvalue
            (id, type), hexvalue = (self.midi_id_map[id1Byte], " ".join(values))
        # If not found, try to match using the first two bytes (id2Bytes)
        elif id2Bytes in self.midi_id_map:
            # If found, extract the (id, type) tuple and remaining values (skipping the first) as hexvalue
            (id, type), hexvalue = (self.midi_id_map[id2Bytes], " ".join(values[1:]))
        else:
            # If no match is found, log a warning and return None
            self.logger.warning(f"No mapped MCU for MIDI message: {message}")
            return None
        
        # If a value map exists for the identified type, use it to get a more meaningful value
        if type in self.midi_value_map:
            value = self.midi_value_map[type].get(hexvalue, None)
        else:
            # If no value map is defined for this type, log the available value maps and return the hexvalue
            #self.logger.info(self.midi_value_map)
            value = hexvalue
        
        # Return the identified type, id, and value as a tuple
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
                self.logger.debug("MCU with semantic but no implementation ") 
            elif type == "fader":
               # self.logger.debug(f"fader {id} = {self.f14bitsToFloat(value)}") 
                self.state_manager.movingfader(id, self.f14bitsToFloat(value), self)
            else:
                self.logger.info(f"No mapped action for {type} '{id}' '{value}'")
        except ValueError as e:
            self.logger.error(e)

    def floatTo14bits(self, value):
        """
        Converts a floating-point number between 0 and 1 to a 14-bit value encoded as a string,
        using only the 7 least significant bits of each byte.

        Parameters:
        - value: float. A floating-point number between 0 and 1.

        Returns:
        - str: A string representing the encoded 14-bit value in the format "ll hh".
        """
        # Ensure the value is within the correct range
        if not 0 <= value <= 1:
            raise ValueError("Value must be between 0 and 1")

        # Convert the floating-point value to a 14-bit integer value
        int_value = int(value * 16383)  # 16383 = 2^14 - 1

        # Extract the low and high 7 bits
        low = int_value & 0x7F  # 7 bits low
        high = (int_value >> 7) & 0x7F  # 7 bits high

        # Format as string
        return f"{low:02X} {high:02X}"

    def f14bitsToFloat(self, value):
        """
        Converts a 14-bit value encoded as a string in the format "ll hh" back to a floating-point number.

        Parameters:
        - value: str. The encoded 14-bit value as a string "ll hh".

        Returns:
        - float: A floating-point number between 0 and 1.
        """
        # Split the string into its low and high parts
        low_str, high_str = value.split()

        # Convert the string values to integers
        low = int(low_str, 16)
        high = int(high_str, 16)

        # Combine the low and high parts to get the original 14-bit integer value
        int_value = (high << 7) + low


        # Convert the 14-bit integer value back to a float
        return int_value / 16380.0  # 16383 = 2^14 - 1
