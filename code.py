"""
Main Application Script for Raspberry Pi Pico Macro Pad

This script configures and runs a custom macro pad using a Raspberry Pi Pico.
It defines button and encoder mappings for various functions including:
- Window management (fullscreen, left/right half)
- Desktop navigation
- Custom key combinations
- Scrolling and zoom control

The script operates in two modes:
1. Production Mode: Normal operation as a macro pad
2. Edit Mode: GPIO diagnostic mode for testing and configuration

Configuration:
    Buttons and encoders are configured through button_map and encoder_map
    dictionaries. Each entry specifies:
    - Physical pin or GPIO number
    - Key mappings or macro functions
    - Long press thresholds (for buttons)
    - Scroll/zoom modes (for encoders)

Dependencies:
    - models.py: Contains the ButtonController and gpio_diag classes
    - env.py: Contains environment configuration and edit mode settings
"""

import gc, time
from adafruit_hid.keycode import Keycode
from models import ButtonController

# Initialize button controller
keyb = ButtonController()

def macro_freemem():
    """Debug macro to print available memory."""
    print("Free memory:", gc.mem_free())

# Define super modifier combination (Ctrl+Alt+Cmd+Shift)
supercombo = (Keycode.CONTROL, Keycode.ALT, Keycode.COMMAND, Keycode.SHIFT)

# Button map using a mix of physical pin numbers and GPIO numbers
# Each button can have:
# - pin: Physical pin number (1-40)
# - gpio: GPIO number (0-28)
# - kbd_key: Key to send when pressed
# - macro_short: Function to call on short press
# - macro_long: Function to call on long press
# - long_press_threshold: Time in seconds for long press
button_map = {
    "Fullscreen": {
        "gpio": 14,  # Physical pin 19
        "macro_short": lambda: keyb.combo_press(supercombo, 'UP_ARROW'),
        "long_press_threshold": 0.25,
        "macro_long":  lambda: keyb.combo_press(supercombo, 'DOWN_ARROW')
    },
    "LeftHalf": {
        "pin": 20,  # GPIO 15
        "macro_short": lambda: keyb.combo_press(supercombo, 'LEFT_ARROW')
    },
    "RightHalf": {
        "gpio": 6,   # Physical pin 9
        "macro_short": lambda: keyb.combo_press(supercombo, 'RIGHT_ARROW')
    },
    "Button 4": {
        "pin": 7,   # GPIO 5
        "macro_short": lambda: keyb.combo_press(supercombo, 'KEYPAD_SIX')
    },
    "Button 5": {
        "gpio": 16,  # Physical pin 21
        "macro_short": lambda: keyb.combo_press(supercombo, 'KEYPAD_FOUR')
    },
    "DesktopLeft": {
        "pin": 6,   # GPIO 4
        "macro_short": lambda: keyb.combo_press(Keycode.CONTROL, 'LEFT_ARROW')
    },
    "DesktopRight": {
        "gpio": 2,   # Physical pin 4
        "macro_short": lambda: keyb.combo_press(Keycode.CONTROL, 'RIGHT_ARROW')
    },
    "Button 8": {
        "gpio": 28,  # Physical pin 34
        "macro_short": lambda: print("Button 8 short macro triggered!"),
        "long_press_threshold": 1.2,
        "macro_long": lambda: print("Button 8 long macro triggered!"),
    },
    "Button 9": {
        "pin": 15,  # GPIO 11
        "kbd_key": "E",
        "long_press_threshold": 4,
        "macro_long": lambda: print("Button 9 long macro triggered!"),
    },
    "Button 10": {
        "gpio": 14,  # Physical pin 19
        "macro_short": lambda: print("Button 10 short macro triggered!"),
        "long_press_threshold": 1.5,
        "macro_long": lambda: (
            print('derp'),
            time.sleep(1),
            print('derp')
        ),
    },
}

# Encoder map using physical pins and GPIO numbers
# Each encoder can have:
# - pin_a/pin_b: Physical pin numbers
# - gpio_a/gpio_b: GPIO numbers
# - scroll_mode: "horizontal", "vertical", "zoom", or "volume"
# - modifier_key: Modifier key for scroll/zoom
encoder_map = {
    "scroll_encoder": {
        "pin_a": 11,  # GPIO 8
        "pin_b": 12,  # GPIO 9
        "scroll_mode": "horizontal",  # Enable horizontal scrolling
        "modifier_key": "SHIFT"      # Use SHIFT key for horizontal scroll (default)
    },
    "zoom_encoder": {
        "gpio_a": 8,  # Physical pin 11
        "gpio_b": 9,  # Physical pin 12
        "scroll_mode": "zoom",    # Enable zoom control
        "modifier_key": "COMMAND" # Use COMMAND key for zoom (since CONTROL is remapped)
    },
    "volume_encoder": {
        "pin_a": 11,  # GPIO 8
        "pin_b": 12,  # GPIO 9
        "scroll_mode": "volume"   # Enable volume control using media keys
    }
}

def main():
    """Initialize and run the macro pad in production mode.
    
    This function:
    1. Configures all buttons from button_map
    2. Configures active encoders from encoder_map
    3. Starts the main event loop
    """
    # Add buttons from the button_map
    for label, config in button_map.items():
        keyb.add_button(
            label=label,
            pin=config.get("pin"),
            gpio=config.get("gpio"),
            kbd_key=config.get("kbd_key"),
            long_press_threshold=config.get("long_press_threshold"),
            macro_short=config.get("macro_short"),
            macro_long=config.get("macro_long"),
        )

    # Add encoders from the encoder_map
    # Only the scroll_encoder is enabled by default, others are commented out
    active_encoders = ["scroll_encoder"]  # Add "zoom_encoder" or "volume_encoder" to enable them
    for label, config in encoder_map.items():
        if label in active_encoders:
            keyb.add_encoder(
                label=label,
                pin_a=config.get("pin_a"),
                pin_b=config.get("pin_b"),
                gpio_a=config.get("gpio_a"),
                gpio_b=config.get("gpio_b"),
                scroll_mode=config.get("scroll_mode"),
                modifier_key=config.get("modifier_key"),
                clockwise_key=config.get("clockwise_key"),
                counterclockwise_key=config.get("counterclockwise_key"),
                clockwise_macro=config.get("clockwise_macro"),
                counterclockwise_macro=config.get("counterclockwise_macro")
            )

    # Run the keyboard controller
    keyb.run()

if __name__ == "__main__":
    # Check if we're in edit mode (GPIO diagnostic mode)
    if edit_mode_switch.value:
        print("Running in EDIT MODE")
        print("USB drive is accessible")
        print("Use GPIO monitor for testing:")
        keyb = gpio_diag()
        keyb.monitor_gpio()
    else:
        print("Running in PRODUCTION MODE")
        main()
