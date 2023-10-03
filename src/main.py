"""
Main execution script for the X-EOS system.
Initializes and runs the system.
"""

from communication.osc_comm import OSCClient
from state.state_manager import StateManager
from mapping.eos_mapping_engine import EOSMappingEngine
from communication.midi_comm import MIDIClient
from mapping.xtouch_mapping_engine import XTouchMappingEngine
import time

if __name__ == "__main__":
    try:
        # Initialization
        state_manager = StateManager()
        osc = OSCClient()
        xtouch_mapping = XTouchMappingEngine(state_manager)
        midi = MIDIClient("config/settings.json", xtouch_mapping.handle_midi_message)
        eos_mapping = EOSMappingEngine(osc_client=osc)
        state_manager.add_observer(eos_mapping)

        # Simulating a key press
        state_manager.key_pressed("LIVE")
        state_manager.key_pressed("LIVE",0)
    
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
        if midi and midi.input_port:
            midi.input_port.close()
        if midi and midi.output_port:
            midi.output_port.close()