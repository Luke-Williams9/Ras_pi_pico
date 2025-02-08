https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/circuitpy-midi-serial


Pinouts

https://www.raspberrypi.com/documentation/microcontrollers/images/pico-pinout.svg

# Raspberry Pi Pico Macro Pad

A customizable macro pad implementation for the Raspberry Pi Pico, featuring support for buttons and rotary encoders. Perfect for window management, media controls, and custom keyboard shortcuts.

## Features

- **Flexible Input Support**
  - Buttons with short and long press detection
  - Rotary encoders with multiple modes
  - Support for both physical pin numbers and GPIO numbers

- **Multiple Operating Modes**
  - Production Mode: Normal macro pad operation
  - Edit Mode: USB drive access and GPIO diagnostics

- **Built-in Functions**
  - Window management (fullscreen, left/right half)
  - Desktop navigation
  - Volume control
  - Horizontal/vertical scrolling
  - Zoom control
  - Custom macro support

## Hardware Requirements

- Raspberry Pi Pico
- Push buttons (momentary switches)
- Rotary encoders (optional)
- SPDT switch for Edit Mode
- Resistors (if using pull-up configuration)
- Breadboard and jumper wires for prototyping

## Software Requirements

- CircuitPython 8.x or later
- Required Libraries:
  - `adafruit_hid`
  - `board`
  - `digitalio`
  - `rotaryio`
  - `storage`
  - `supervisor`
  - `usb_cdc`

## Installation

1. **Install CircuitPython**
   - Download the latest CircuitPython UF2 file for Raspberry Pi Pico
   - Hold the BOOTSEL button while connecting the Pico to your computer
   - Copy the UF2 file to the RPI-RP2 drive that appears

2. **Install Required Libraries**
   - Download the CircuitPython library bundle
   - Copy the following files to the `lib` folder on your CIRCUITPY drive:
     - `adafruit_hid`

3. **Copy Project Files**
   - Copy all project files to the root of your CIRCUITPY drive:
     - `boot.py`
     - `code.py`
     - `env.py`
     - `models.py`

## Hardware Setup

1. **Edit Mode Switch**
   - Connect GPIO22 (Physical Pin 29) to one terminal of an SPDT switch
   - Connect 3.3V to the other terminal
   - The switch enables/disables USB drive access and diagnostic mode

2. **Buttons**
   - Connect one side of each button to GND
   - Connect the other side to a GPIO pin
   - Configure the pin numbers in `code.py` under `button_map`

3. **Encoders**
   - Connect encoder GND to GND
   - Connect encoder A and B pins to GPIO pins
   - Configure the pin numbers in `code.py` under `encoder_map`

## Configuration

1. **Button Configuration**
   Edit `code.py` to configure buttons:
   ```python
   button_map = {
       "ButtonName": {
           "pin": 20,  # Physical pin number
           # or
           "gpio": 15,  # GPIO number
           "kbd_key": "A",  # For simple key press
           # or
           "macro_short": lambda: some_function(),  # For custom function
           "long_press_threshold": 0.5,  # Optional
           "macro_long": lambda: other_function()  # Optional
       }
   }
   ```

2. **Encoder Configuration**
   Edit `code.py` to configure encoders:
   ```python
   encoder_map = {
       "EncoderName": {
           "pin_a": 11,  # Physical pin for A
           "pin_b": 12,  # Physical pin for B
           # or
           "gpio_a": 8,  # GPIO number for A
           "gpio_b": 9,  # GPIO number for B
           "scroll_mode": "horizontal",  # horizontal/vertical/zoom/volume
           "modifier_key": "SHIFT"  # Optional modifier key
       }
   }
   ```

## Usage

1. **Normal Operation (Production Mode)**
   - Set the edit mode switch to OFF
   - The device will function as a macro pad
   - LED will blink to indicate successful initialization

2. **Configuration Mode (Edit Mode)**
   - Set the edit mode switch to ON
   - Connect the Pico to your computer
   - The CIRCUITPY drive will appear
   - Edit configuration files as needed
   - GPIO diagnostic tool will be active for testing

3. **GPIO Diagnostics**
   - In Edit Mode, the GPIO monitor will show pin state changes
   - Use this to test buttons and encoders
   - Format: `GPIO XX: HIGH/LOW`

## Troubleshooting

1. **USB Drive Not Appearing**
   - Ensure edit mode switch is ON
   - Check edit mode switch connections
   - Verify `boot.py` is present on the device

2. **Buttons/Encoders Not Working**
   - Use Edit Mode to run GPIO diagnostics
   - Verify pin numbers in configuration
   - Check physical connections
   - Ensure GND connections are solid

3. **Code Not Running**
   - Check if `code.py` is present
   - Verify all required libraries are installed
   - Look for errors in the serial console (Edit Mode)

## Contributing

Feel free to submit issues and pull requests for:
- New features
- Bug fixes
- Documentation improvements
- Hardware configuration examples

## License

This project is released under the MIT License. See LICENSE file for details.