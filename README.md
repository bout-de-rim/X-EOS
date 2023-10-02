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

## Contribution

Contributions are always welcome! Please fork the repository, make your changes, and submit a pull request.

## License

[MIT License](LICENSE) - See the LICENSE file for details.

## Acknowledgments

- The wonderful OpenAI community for guidance and discussions.
- [ETC](https://www.etcconnect.com/) and [Behringer](https://www.behringer.com/) for their incredible products.

---

Replace `[repository_url]` with the actual URL of your project's repository. The `#project-skeleton-link` should be linked to a detailed documentation or a wiki page that explains the project structure if necessary. Modify and expand as you see fit!