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

    def __init__(self, logger, config_file, message_callback=example_callback):
        """
        Initializes the MIDIClient.

        Parameters:
        - logger: Logger - The logger object for logging messages.
        - config_file: str - The path to the configuration file.
        - message_callback: function - The callback function for handling received MIDI messages.
        """
        self.config = read_json(config_file)
        self.input_device_patterns = self.config.get("MIDI", {}).get("input_device_pattern", ".*")
        self.output_device_patterns = self.config.get("MIDI", {}).get("output_device_pattern", ".*")
        self.input_port = None
        self.output_port = None
        self.message_callback = message_callback
        self.logger = logger

        self.initialize_midi_ports()

    def initialize_midi_ports(self):
        input_ports, output_ports = self.get_available_midi_ports()
        self.logger.info(f"Available MIDI input ports: {input_ports}")
        self.logger.info(f"Available MIDI output ports: {output_ports}")
        
        # Initialize input port
        for pattern in self.input_device_patterns:
            matching_input_ports = [port for port in input_ports if re.match(pattern, port)]
            if matching_input_ports:
                try:
                    self.logger.info(f"Trying MIDI input port: {matching_input_ports[0]}.")
                    self.input_port = mido.open_input(matching_input_ports[0], callback=self.message_callback)
                    self.logger.info(f"Initialized MIDI input port: {matching_input_ports[0]}.")
                    break
                except IOError as e:
                    self.logger.warning(f"Error opening MIDI input port: {e}. Trying next available port...")
        else:
            raise ValueError("No MIDI input ports match the given patterns or all ports are in use.")

        # Initialize output port
        for pattern in self.output_device_patterns:
            matching_output_ports = [port for port in output_ports if re.match(pattern, port)]
            if matching_output_ports:
                try:
                    self.logger.info(f"Trying MIDI output port: {matching_output_ports[0]}.")
                    self.output_port = mido.open_output(matching_output_ports[0])
                    self.logger.info(f"Initialized MIDI output port: {matching_output_ports[0]}.")
                    self.send_midi_hex("F0 00 00 66 14 13 00 F7")
                    break
                except IOError as e:
                    self.logger.warning(f"Error opening MIDI output port: {e}. Trying next available port...")
        else:
            raise ValueError("No MIDI output ports match the given patterns or all ports are in use.")


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
