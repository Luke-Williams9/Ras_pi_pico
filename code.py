import time
import gc
from adafruit_hid.keycode import Keycode
import rotaryio
from models import ButtonController, gpio_diag

# Initialize and load button definitions
keyb = ButtonController()
def macro_freemem():
    print("Free memory:", gc.mem_free())

    
supercombo = (Keycode.CONTROL, Keycode.ALT, Keycode.COMMAND, Keycode.SHIFT)

# Based on hotkeys I configured in Rectangle
button_map = {
    "Fullscreen": {
        "pin": 14,
        "macro_short": lambda: keyb.combo_press(supercombo, 'UP_ARROW'),
        "long_press_threshold": 0.25,
        "macro_long":  lambda: keyb.combo_press(supercombo, 'DOWN_ARROW')
    },
    "LeftHalf": {
        "pin": 15,
        "macro_short": lambda: keyb.combo_press(supercombo, 'LEFT_ARROW')
    },
    "RightHalf": {
        "pin": 5,
        "macro_short": lambda: keyb.combo_press(supercombo, 'RIGHT_ARROW')
    },
    "Button 4": {
        "pin": 3,
        "macro_short": lambda: keyb.combo_press(supercombo, 'KEYPAD_SIX')
    },
    "Button 5": {
        "pin": 16,
        "macro_short": lambda: keyb.combo_press(supercombo, 'KEYPAD_FOUR')
    },
    "DesktopLeft": {
        "pin": 2,
        "macro_short": lambda: keyb.combo_press(Keycode.CONTROL, 'LEFT_ARROW')
        
    },
    "DesktopRight": {
        "pin": 0,
        "macro_short": lambda: keyb.combo_press(Keycode.CONTROL, 'RIGHT_ARROW')
    },
    "Button 8": {
        "pin": 28,
        "macro_short": lambda: print("Button 8 short macro triggered!"),
        "long_press_threshold": 1.2,
        "macro_long": lambda: print("Button 8 long macro triggered!"),
    },
    "Button 9": {
        "pin": 10,
        "kbd_key": "E",
        "long_press_threshold": 4,
        "macro_long": lambda: print("Button 9 long macro triggered!"),
    },
    "Button 10": {
        "pin": 11,
        "macro_short": lambda: print("Button 10 short macro triggered!"),
        "long_press_threshold": 1.5,
        "macro_long": lambda: (
            print('derp'),
            time.sleep(1),
            print('derp')
        ),
    },
}

keyb = ButtonController()

# Add buttons from the button_map
for label, config in button_map.items():
    keyb.add_button(
        pin_number=config["pin"],
        label=label,
        kbd_key=config.get("kbd_key"),
        long_press_threshold=config.get("long_press_threshold"),
        macro_short=config.get("macro_short"),
        macro_long=config.get("macro_long"),
    )

# Add rotary encoder
keyb.add_encoder(
    pin_a=8,              # GP8
    pin_b=9,              # GP9
    label="test_encoder",
    clockwise_key="A",        # Press 'A' when turned clockwise
    counterclockwise_key="B"  # Press 'B' when turned counter-clockwise
)

keyb.run()
# keyb = gpio_diag()
# keyb.monitor_gpio()




# type: ignore # Provide a way to enable USB storage after its been disabled
# storage_unlock_pin = board.GP4
# # this is pseudocode:
# if storage_unlock_pin is True
#	import os
#	os.remove('boot.py')
#	os.hardboot()
