# X-EOS: X-Touch to EOS Integration

X-EOS is a Python-based driver that bridges the gap between Behringer's X-Touch controller and the ETC EOS lighting console. By leveraging the power of OSC and MIDI communication, X-EOS replicates the physical controls of the standard EOS console on the X-Touch.

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Tool and Library Selection](#tool-and-library-selection)
  - [Testing with pytest](#testing-with-pytest)
- [Contribution](#contribution)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- **X-Touch Integration**: Seamlessly map X-Touch's faders, rotary encoders, VU-meters, and other controls to EOS functionalities.
- **Bi-directional Communication**: Uses OSC for EOS and MIDI for X-Touch in its MCU emulation mode.
- **Scalability**: An integrated plugin system and configurable mappings ensure adaptability for future needs.

## Getting Started

### Prerequisites

- Python 3.x
- An X-Touch controller
- EOS Nomad software

### Installation

1. Clone the X-EOS repository:
```bash
git clone bout-de-rim/X-EOS
```
2. Navigate to the project directory and install the required packages:
```bash
cd X-EOS
pip install -r requirements.txt
```
### Configuration

Modify the `settings.json` file within the `config` directory to match your OSC and MIDI setups. Ensure the correct hostname, port, and device names are set.

Configure EOS in Setup>System>ShowControl>OSC : 
* Enable RX and TX, 
* configure RX port accordingly to settings.json, 
* configure TX port accordingly to what says X-EOS at launch. 

## Usage

Run the main script to initialize the X-EOS system:
```bash
python main.py
```

## Development

### Project Structure

Refer to the provided [project skeleton](#project-skeleton-link) for a detailed breakdown of the codebase's organization and documentation.

### Tool and Library Selection

The project primarily uses `python-osc` for OSC communication, `mido` for MIDI operations, and other Python libraries for functionalities like JSON handling, observer pattern implementation, and multi-threading.

### Testing with pytest

X-EOS adopts `pytest` as its primary testing framework. 

To run the tests:

```bash
pytest
```

For a detailed output, use:

```bash
pytest -v
```

**Note:** If you face any import issues related to module resolution, ensure to adjust your `PYTHONPATH` to include the `src` directory:

```bash
$env:PYTHONPATH += ";path-to-your-X-EOS-folder\src"
```

Replace `path-to-your-X-EOS-folder` with the actual path to the `X-EOS` project directory on your system.

## Contribution

Contributions are always welcome! Please fork the repository, make your changes, and submit a pull request.

## License

[MIT License](LICENSE) - See the LICENSE file for details.

