import gc, time
from adafruit_hid.keycode import Keycode
from models import ButtonController

# Initialize and load button definitions
keyb = ButtonController()
def macro_freemem():
    print("Free memory:", gc.mem_free())

# A key combo to configure your shortcuts and hotkeys with. Make as many of these as you like
supercombo = (Keycode.CONTROL, Keycode.ALT, Keycode.COMMAND, Keycode.SHIFT)

# Button map using a mix of physical pin numbers and GPIO numbers for examples
button_map = {
#     "Fullscreen": {
#         "gpio": 14,  # Physical pin 19
#         "macro_press": lambda: keyb.combo_press(supercombo, 'UP_ARROW'),
#         "long_press_threshold": 0.25,
#         "macro_long":  lambda: keyb.combo_press(supercombo, 'DOWN_ARROW')
#     },
#     "LeftHalf": {
#         "pin": 20,  # GPIO 15
#         "macro_press": lambda: keyb.combo_press(supercombo, 'LEFT_ARROW')
#     },
#     "RightHalf": {
#      e   "gpio": 23,   # Physical pin 9
#         "macro_presswn": lambda: keyb.combo_press(supercombo, 'RIGHT_ARROW')
#     },
    "Button 4": {
        "gpio": 22,
        "macro_press": lambda: print("GPIO22 SHORT"),
        "long_press_threshold": 0.4,
        "macro_long": lambda: print("GPIO22 LONG"),
        "macro_release": lambda: print("GPIO22 RELEASE"),
        "fuckyou": "FUCKYOUUUUUU"
    },
#     "Button 5": {
#         "gpio": 16,  # Physical pin 21
#         "macro_press": lambda: keyb.combo_press(supercombo, 'KEYPAD_FOUR')
#     },
#     "DesktopLeft": {
#         "pin": 6,   # GPIO 4
#         "macro_press": lambda: keyb.combo_press(Keycode.CONTROL, 'LEFT_ARROW')
#     },
#     "DesktopRight": {
#         "gpio": 2,   # Physical pin 4
#         "macro_press": lambda: keyb.combo_press(Keycode.CONTROL, 'RIGHT_ARROW')
#     },
#     "Button 8": {
#         "gpio": 28,  # Physical pin 34
#         "macro_press": lambda: print("Button 8 short macro triggered!"),
#         "long_press_threshold": 1.2,
#         "macro_long": lambda: print("Button 8 long macro triggered!"),
#     },
#     "Button 9": {
#         "pin": 15,  # GPIO 11
#         "kbd_key": "E",
#         "long_press_threshold": 4,
#         "macro_long": lambda: print("Button 9 long macro triggered!"),
#     },
#     "Button 10": {
#         "gpio": 13,  
#         "macro_press": lambda: print("Button 10 short macro triggered!"),
#         "long_press_threshold": 1.5,
#         "macro_long": lambda: (
#             print('derp'),
#             time.sleep(1),
#             print('derp')
#         ),
#     },
}

# Encoder map using physical pins and GPIO numbers
encoder_map = {
    "scroll_encoder": {
        "pin_a": 11,  # GPIO 8
        "pin_b": 12,  # GPIO 9
        "scroll_mode": "horizontal",  # Enable horizontal scrolling
        "modifier_key": "SHIFT"      # Use SHIFT key for horizontal scroll (default)
    }
#     "zoom_encoder": {
#         "gpio_a": 8,  # Physical pin 11
#         "gpio_b": 9,  # Physical pin 12
#         "scroll_mode": "zoom",    # Enable zoom control
#         "modifier_key": "COMMAND" # Use COMMAND key for zoom (since CONTROL is remapped)
#     }
#     "volume_encoder": {
#         "pin_a": 11,  # GPIO 8
#         "pin_b": 12,  # GPIO 9
#         "scroll_mode": "volume"   # Enable volume control using media keys
#     }
}

def main():
    # Add buttons from the button_map
    for label, config in button_map.items():
        keyb.add_button(label, **config)
        # keyb.add_button(
        #     label=label,
        #     pin=config.get("pin"),
        #     gpio=config.get("gpio"),
        #     kbd_key=config.get("kbd_key"),
        #     long_press_threshold=config.get("long_press_threshold"),
        #     macro_press=config.get("macro_press"),
        #     macro_long=config.get("macro_long"),
        #     macro_release=config.get("macro_release")
        # )

    # Add encoders from the encoder_map
    # Only the scroll_encoder is enabled by default, others are commented out
    active_encoders = ["scroll_encoder"]  # Add "zoom_encoder" or "volume_encoder" to enable them
    for label, config in encoder_map.items():
        if label in active_encoders:
            keyb.add_encoder(label, **config)
            # keyb.add_encoder(
            #     label=label,
            #     pin_a=config.get("pin_a"),
            #     pin_b=config.get("pin_b"),
            #     gpio_a=config.get("gpio_a"),
            #     gpio_b=config.get("gpio_b"),
            #     scroll_mode=config.get("scroll_mode"),
            #     modifier_key=config.get("modifier_key"),
            #     clockwise_key=config.get("clockwise_key"),
            #     counterclockwise_key=config.get("counterclockwise_key"),
            #     clockwise_macro=config.get("clockwise_macro"),
            #     counterclockwise_macro=config.get("counterclockwise_macro")
            # )

    # Run the keyboard controller
    keyb.run()

if __name__ == "__main__":
    main()
