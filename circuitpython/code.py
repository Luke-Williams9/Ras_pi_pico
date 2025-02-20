import gc, time
from adafruit_hid.keycode import Keycode
from models import ButtonController

# Initialize and load button definitions
keyb = ButtonController()

# A key combo to configure your shortcuts and hotkeys with. Make as many of these as you like
supercombo = (Keycode.CONTROL, Keycode.ALT, Keycode.COMMAND, Keycode.SHIFT)

# a1 a2 a3 a4
# b1 b2 b3 b4
# c1 c2 c3 c4
# d1 d2 d3 d4
# e1 e2 e3 e4
# f1 f2 f3 f4


# "Btn_a1": {
#         "gpio": 0,
#         "macro_press": lambda: print("short macro triggered"),
#         "long_press_threshold": 1.2,
#         "macro_long": lambda: print("long macro triggered"),
#		  "macro_release": lambda: print("release macro triggered")
#     }

# Button map using a mix of physical pin numbers and GPIO numbers for examples
button_map = {
    "Btn_a1_DesktopLeft": {
        "gpio": 13,
        "macro_press": lambda: keyb.combo_press(Keycode.CONTROL, 'LEFT_ARROW')
    },
    "Btn_a2_DesktopRight": {
        "gpio": 6,
        "macro_press": lambda: keyb.combo_press(Keycode.CONTROL, 'RIGHT_ARROW')
    },
    "Btn_a4_Fullscreen": {
        "gpio": 14,
        "macro_press": lambda: keyb.combo_press(supercombo, 'UP_ARROW'),
        "long_press_threshold": 0.25,
        "macro_long":  lambda: keyb.combo_press(supercombo, 'DOWN_ARROW')
    },
    "Button b1": {
        "gpio": 11,
        "macro_press": lambda: print("Button 8 short macro triggered!"),
        "long_press_threshold": 1.2,
        "macro_long": lambda: print("Button 8 long macro triggered!")
    },
    "Btn_c3_TopHalf": {
        "gpio": 10,
        "macro_press": lambda: keyb.combo_press(supercombo, 'LEFT_ARROW')
    },
    "Btn_d2_LeftHalf": {
        "gpio": 4,
        "macro_press": lambda: keyb.combo_press(supercombo, 'LEFT_ARROW')
    },
    "Btn_d3_BottomHalf": {
        "gpio": 12,
        "macro_press": lambda: keyb.combo_press(supercombo, 'DOWN_ARROW')
    },
    "Btn_d4_RightHalf": {
        "gpio": 15,
        "macro_press": lambda: keyb.combo_press(supercombo, 'RIGHT_ARROW')
    },
    "Btn_e1": {
        "gpio": 5,
        "macro_press": lambda: print("GPIO22 SHORT"),
        "long_press_threshold": 0.4,
        "macro_long": lambda: print("GPIO22 LONG"),
        "macro_release": lambda: print("GPIO22 RELEASE")
    },
    "Btn_f1": {
        "gpio": 3,
        "macro_press": lambda: keyb.combo_press(supercombo, 'KEYPAD_FOUR')
    }

#     "DesktopLeft": {
#         "pin": 6,   # GPIO 4
#         "macro_press": lambda: keyb.combo_press(Keycode.CONTROL, 'LEFT_ARROW')
#     },
#     "DesktopRight": {
#         "gpio": 2,   # Physical pin 4
#         "macro_press": lambda: keyb.combo_press(Keycode.CONTROL, 'RIGHT_ARROW')
#     },

#     "ScrollZoom_Button": {
#         "gpio": 2,
#         "macro_press": lambda: print("derp")
#     }
#     "ScrollEnc_Button": {
#         "gpio": 20,  
#         "macro_press": lambda: print("Button 10 short macro triggered!")
# 
#     }
}

# Encoder map using physical pins and GPIO numbers
encoder = {
    "gpio_a": 1,
    "gpio_b": 0,
    "gpio_button": 2,
    "modes": ["horizontal","zoom"]
}


# encoder_map = {
#     "scroll_encoder": {
#         "gpio_a": 0,
#         "gpio_b": 1,
#         "scroll_mode": "horizontal",  # Enable horizontal scrolling
#         "modifier_key": "SHIFT"      # Use SHIFT key for horizontal scroll (default)
#     }
#      "zoom_encoder": {
#         "gpio_a": 20,
#         "gpio_b": 21,
#         "scroll_mode": "zoom",    # Enable zoom control
#         "modifier_key": "COMMAND" # Use COMMAND key for zoom (since CONTROL is remapped)
#     }
# }

def main():
    print('-------------------------------------------------')
    print("Starting button controller...")

    # Only run one part at a time to isolate the problem
    print('-----------------------------')
    print("Adding buttons...")
    for label, config in button_map.items():
        print('------------------')
        print(f"Adding button: {label}")
        keyb.add_button(label, **config)
        time.sleep(0.01)
    
    print('---------------')
    print(f"Adding encoder")
    keyb.add_encoder(**encoder)
    time.sleep(0.01)

    print("Starting keyb.run()...")
    keyb.run()

if __name__ == "__main__":
    main()


