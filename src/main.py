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
import logging
from gui import run_gui
import threading

def start_osc_server(osc):
    try:
        osc.start_server("/eos", eos_mapping.eos_osc_handler)
        while True:
            time.sleep(1)  # Maintient le serveur actif sans surcharger le processeur
    except Exception as e:
        logger.error(f"OSC Server Error: {e}")
    finally:
        logger.info("OSC Server stopped.")

if __name__ == "__main__":
    # Configuration du logger
    logger = logging.getLogger('X-EOS')
    logger.setLevel(logging.DEBUG)  # Définir le niveau de log le plus bas ici

    # Handler de console (sortie standard)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Ou autre niveau selon les besoins

    # Format du log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Ajouter le handler de console par défaut
#    logger.addHandler(console_handler)


    try:
        # Initialization
        state_manager = StateManager(logger)
        osc = OSCClient(logger)
        xtouch_mapping = XTouchMappingEngine(logger, state_manager)
        midi = MIDIClient(logger, "config/settings.json", xtouch_mapping.handle_midi_message)
        xtouch_mapping._midi_comm = midi
        xtouch_mapping.init_xtouch()
        eos_mapping = EOSMappingEngine(logger, osc_client=osc, state_manager=state_manager)
        state_manager.add_observer(eos_mapping)
        state_manager.add_observer(xtouch_mapping)
        state_manager.eos = eos_mapping
        state_manager.xtouch = xtouch_mapping
        logger.info(f"State Manager initialized with {len(state_manager._observers)} observers.")
       # osc.start_server("/eos", eos_mapping.eos_osc_handler)
        osc_thread = threading.Thread(target=lambda: start_osc_server(osc), daemon=True)
        osc_thread.start()
        time.sleep(1)
        state_manager.setFaderPage(1)

        # Simulating a key press
        #state_manager.key_pressed("LIVE")
        #state_manager.key_pressed("LIVE",0)
    
        logger.info("Waiting for MIDI messages. ")

        # Import et exécution de la GUI ici, si pas en mode headless
        run_gui(logger)

    except ValueError as e:
        logger.error(e)
    except KeyboardInterrupt:
        logger.info("Exiting.")
    finally:
        # Cleanup: Ensure to close MIDI ports properly to free up resources.
        if midi and midi.input_port:
            midi.input_port.close()
        if midi and midi.output_port:
            midi.output_port.close()