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
    - listen_midi(): Continuously listen to MIDI messages from X-Touch.
    """

    def __init__(self, config_file, message_callback=None):
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

    def listen_midi(self):
        """
        Continuously listen to MIDI messages from X-Touch.
        Note: This function should ideally run in a separate thread to prevent blocking.
        """
        for message in self.input_port.iter_pending():
            self.process_midi_message(message)

    def process_midi_message(self, message):
        """
        Process a received MIDI message.
        To be implemented according to the application needs.

        Parameters:
        - message: MidiMessage - The received MIDI message.
        """
        # Implementation according to application needs
        pass


# Example usage and testing code
def example_callback(msg):
    """
    An example callback function that prints the received MIDI message.

    Parameters:
    - msg: MidiMessage - The received MIDI message.
    """
    print(f"Received: {msg}")

# Example usage and testing code
if __name__ == "__main__":
    try:
        client = MIDIClient("config/settings.json", message_callback=example_callback)

        # Create a message
        msg = mido.Message('note_on', note=60)

        # Send a message
        client.send_midi_message(msg)

        print("Waiting for MIDI messages. Press Ctrl+C to exit.")
        while True:
            # The application is kept alive and running by this loop.
            # The callback handles all incoming messages.
            # You may also add additional periodic checks or functionality here.
            time.sleep(1)  # Prevents CPU from running at 100% and provides a slight delay in the loop.

    except ValueError as e:
        print(e)
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        # Cleanup: Ensure to close MIDI ports properly to free up resources.
        if client and client.input_port:
            client.input_port.close()
        if client and client.output_port:
            client.output_port.close()