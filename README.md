# NetVoice

A simple VoIP (Voice over IP) application implemented in Python for real-time voice communication over networks.

## Features

- Real-time audio capture and playback
- UDP-based network transmission
- Support for multiple audio devices
- Basic audio compression
- Low-latency communication

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/NetVoice.git
cd NetVoice
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:

```bash
python src/main.py
```

2. Select your audio input device when prompted

3. Connect to another NetVoice client by entering their IP address

## Development

- Python 3.8 or higher required
- See requirements.txt for package dependencies
- Run tests using pytest: `pytest tests/`

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
