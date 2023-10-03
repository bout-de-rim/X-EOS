"""
midi_comm.py
Handles all MIDI communications related to the X-Touch using the mido library.

Classes:
- MIDIClient: Establishes and manages a MIDI client for communication with X-Touch.
"""

import mido
import re
from mido import MidiFile, MidiTrack
from utils import read_json
import time


# Example usage and testing code
def example_callback(msg):
    """
    An example callback function that prints the received MIDI message.

    Parameters:
    - msg: MidiMessage - The received MIDI message.
    """
    print(f"Received: {msg}")

class MIDIClient:
    """
    Establishes and manages a MIDI client for communication with X-Touch.

    Attributes:
    - device_name: The MIDI device name.
    - input_port: The input MIDI port.
    - output_port: The output MIDI port.
    
    Methods:
    - get_available_midi_ports(): Retrieve available MIDI ports.
    - initialize_midi_ports(): Initialize input and output MIDI ports.
    - send_midi_message(): Send a MIDI message to X-Touch.
    """

    def __init__(self, config_file, message_callback=example_callback):
        """

        """
        self.config = read_json(config_file)
        self.device_pattern = self.config.get("MIDI", {}).get("device_pattern", ".*")
        self.input_port = None
        self.output_port = None
        self.message_callback = message_callback

        self.initialize_midi_ports()

    def initialize_midi_ports(self):
        input_ports, output_ports = self.get_available_midi_ports()

        matching_input_ports = [port for port in input_ports if re.match(self.device_pattern, port)]
        matching_output_ports = [port for port in output_ports if re.match(self.device_pattern, port)]

        if not matching_input_ports or not matching_output_ports:
            raise ValueError(f"No MIDI ports match the pattern '{self.device_pattern}'.")
        
        # Selecting the first matching port for simplicity, can be adjusted based on requirements
        self.input_port = mido.open_input(matching_input_ports[0], callback=self.message_callback)
        self.output_port = mido.open_output(matching_output_ports[0])

        print(f"Initialized MIDI ports: {matching_input_ports[0]} (input) and {matching_output_ports[0]} (output).")

    @staticmethod
    def get_available_midi_ports():
        """
        Retrieve available MIDI ports.

        Returns:
        - input_ports: list - Names of available input ports.
        - output_ports: list - Names of available output ports.
        """
        input_ports = mido.get_input_names()
        output_ports = mido.get_output_names()
        
        return input_ports, output_ports

    def send_midi_message(self, message):
        """
        Send a MIDI message to X-Touch.

        Parameters:
        - message: MidiMessage - A mido.MidiMessage object to be sent.
        """
        self.output_port.send(message)

    def send_midi_hex(self, message):
        """
        Send a MIDI message to X-Touch.

        Parameters:
        - message: bytes - A bytes object to be sent.
        """
        self.send_midi_message(mido.Message.from_hex(message))
