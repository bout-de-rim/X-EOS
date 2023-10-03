import pytest
import mido
from unittest.mock import Mock, patch
from communication.midi_comm import MIDIClient

# Constants for the tests
TEST_DEVICE_NAME = "TestMIDIDevice"

# Mocking midi port objects
mock_input_port = Mock(spec=mido.ports.BaseInput)
mock_output_port = Mock(spec=mido.ports.BaseOutput)

@pytest.fixture
def mock_midi_ports():
    with patch("mido.get_input_names", return_value=[TEST_DEVICE_NAME]), \
         patch("mido.get_output_names", return_value=[TEST_DEVICE_NAME]), \
         patch("mido.open_input", return_value=mock_input_port), \
         patch("mido.open_output", return_value=mock_output_port):
        yield

@pytest.fixture
def midi_client(mock_midi_ports):
    return MIDIClient(TEST_DEVICE_NAME)

def test_midi_client_initialization(mock_midi_ports):
    client = MIDIClient(TEST_DEVICE_NAME)
    assert client.device_name == TEST_DEVICE_NAME

def test_midi_client_wrong_device():
    with pytest.raises(ValueError):
        client = MIDIClient("NonExistentDevice")

def test_send_midi_message(midi_client):
    test_message = mido.Message('note_on', note=60)
    midi_client.send_midi_message(test_message)
    midi_client.output_port.send.assert_called_once_with(test_message)

def test_listen_midi(midi_client):
    # Mock a MIDI message and its processor
    test_message = mido.Message('note_on', note=60)
    midi_client.input_port.iter_pending = Mock(return_value=iter([test_message]))

    with patch.object(midi_client, "process_midi_message") as mock_processor:
        midi_client.listen_midi()
        mock_processor.assert_called_once_with(test_message)
