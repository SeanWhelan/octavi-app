# Udev Rules Manager for Octavi IFR1

This application provides a graphical interface to manage udev rules for Octavi IFR1 devices. It allows users to list, create, and manage udev rules, as well as find and set permissions for Octavi devices.

## Features

- List Octavi-related udev rules
- Reload udev rules
- Trigger udev rules
- Show hidraw device permissions
- Display hidraw-related kernel messages
- Create new udev rules for Octavi devices
- Find Octavi devices and set permissions

## Requirements

- Python 3.6+
- PyQt6
- Linux operating system with udev

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/SeanWhelan/octavi-app.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python octavi-app.py
   ```

## Usage

Launch the application and use the buttons in the interface to perform various actions. The right panel provides instructions for each feature.

Note: Some actions require sudo privileges and will prompt for your password.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
