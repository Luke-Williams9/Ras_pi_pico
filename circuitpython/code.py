import gc, time
from adafruit_hid.keycode import Keycode
from models import ButtonController

# Initialize and load button definitions
keyb = ButtonController()

# A key combo to configure your shortcuts and hotkeys with. Make as many of these as you like

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

supercombo = (Keycode.CONTROL, Keycode.ALT, Keycode.COMMAND, Keycode.SHIFT)
ctrl = Keycode.CONTROL
cmd = Keycode.COMMAND

button_map = {
    "Btn_a1_Lock": {
        "gpio": 9,
        "macro_press": lambda: keyb.combo_press((ctrl,cmd),'Q')
#        "long_press_theshold": 1,
#        "macro_long": lambda: self.keyboard.press("ESCAPE"); time.sleep(.05); self.keyboard.release("ESCAPE")
    },
    "Btn_a3_DesktopLeft": {
        "gpio": 10,
        "macro_press": lambda: keyb.combo_press(ctrl, 'LEFT_ARROW')        
    },
    "Btn_a4_DesktopRight": {
        "gpio": 11,
        "macro_press": lambda: keyb.combo_press(ctrl, 'RIGHT_ARROW')
    },
    "Btn_b1_noneYet": {
        "gpio": 13,
        "macro_press": lambda: keyb.combo_press(ctrl, 'RIGHT_ARROW')
    },
    "Btn_b3_Fullscreen": {
        "gpio": 14,
        "macro_press": lambda: keyb.combo_press(supercombo, 'KEYPAD_NINE'),
        "long_press_threshold": 0.25,
        "macro_long":  lambda: keyb.combo_press(supercombo, 'KEYPAD_SEVEN')
    },
    "Btn_c2_LeftThird": {
        "gpio": 7,
        "macro_press": lambda: keyb.combo_press(supercombo, 'KEYPAD_ONE')
    },
    "Btn_c3_TopHalf": {
        "gpio": 5,
        "macro_press": lambda: keyb.combo_press(supercombo, 'UP_ARROW')
    },
    "Btn_c4_RightThird": {
        "gpio": 6,
        "macro_press": lambda: keyb.combo_press(supercombo, 'KEYPAD_THREE')
    },
    "Btn_d2_LeftHalf": {
        "gpio": 3,
        "macro_press": lambda: keyb.combo_press(supercombo, 'LEFT_ARROW')
    },
    "Btn_d3_BottomHalf": {
        "gpio": 4,
        "macro_press": lambda: keyb.combo_press(supercombo, 'DOWN_ARROW')
    },
    "Btn_d4_RightHalf": {
        "gpio": 2,
        "macro_press": lambda: keyb.combo_press(supercombo, 'RIGHT_ARROW')
    },
    "Btn_f1_Terminal": {
        "gpio": 17,
        "macro_press": lambda: keyb.combo_press(supercombo, 'T') 
    },
    "Btn_f3_MissionControl": {
        "gpio": 16,
        "macro_press": lambda: keyb.combo_press(ctrl, "UP_ARROW"),
    },
    "Btn_f4_Spotlight": {
        "gpio": 19,
        "macro_press": lambda: keyb.combo_press(cmd, 'SPACEBAR')
    },
    "Btn_f3_AppExpose": {
        "gpio": 15,
        "macro_press": lambda: keyb.combo_press(ctrl, 'DOWN_ARROW')
    }
}

# Encoder map using physical pins and GPIO numbers
# enc_old = {
#     "gpio_a": 1,
#     "gpio_b": 0,
#     "gpio_button": 2,
#     "modes": ["horizontal","zoom"]
# }


encoder = {
    "gpio_a": 26,      ##
    "gpio_b": 27,      ##
    "gpio_button": 28, ##
    "gpio_led1": 0,    ##
    "gpio_led2": 1     ##
}

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



