import time
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
import board
import digitalio


class ButtonController:
    def __init__(self):
        self.buttons = {}
        self.long_press_buttons = {}
        self.keyboard = Keyboard(usb_hid.devices)

    def add_button(self, pin_number, label, key):
        pin = getattr(board, f"GP{pin_number}")
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.DOWN
        self.buttons[label] = {
            'button': button,
            'key': getattr(Keycode, key),
            'pressed': False
        }

    def add_longpress(self, pin_number, label, threshold=1.0, callback=None):
        pin = getattr(board, f"GP{pin_number}")
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.DOWN
        self.long_press_buttons[label] = {
            'button': button,
            'pressed': False,
            'press_time': None,
            'threshold': threshold,
            'callback': callback
        }

    def run(self):
        while True:
            # Handle normal button presses - single keys
            for label, info in self.buttons.items():
                button = info['button']
                key = info['key']
                try:
                    if button.value and not info['pressed']:
                        self.keyboard.press(key)
                        info['pressed'] = True
                    elif not button.value and info['pressed']:
                        self.keyboard.release(key)
                        info['pressed'] = False
                except ValueError as e:
                    print(f"Error: {e}")

            # Handle long press buttons - trigger a macro function
            for label, info in self.long_press_buttons.items():
                button = info['button']
                try:
                    if button.value and not info['pressed']:
                        info['pressed'] = True
                        info['press_time'] = time.monotonic()
                    elif button.value and info['pressed']:
                        if time.monotonic() - info['press_time'] > info['threshold']:
                            if info['callback']:
                                info['callback']()
                            info['press_time'] = time.monotonic()  # Reset press time to avoid multiple triggers
                    elif not button.value and info['pressed']:
                        info['pressed'] = False
                        info['press_time'] = None
                except ValueError as e:
                    print(f"Error: {e}")

            time.sleep(0.01)

keyb = ButtonController()


# Example usage
def macro_one():
    print("Long press action triggered!")

keyb = ButtonController()

# .add_button(GP#, Label, Keycode)
keyb.add_button(9, "Jump", 'TWO')
# .add_longpress(GP#, Label, threshold in seconds, function to trigger)
keyb.add_longpress(10, "Shoot", threshold=2.0, callback=macro_one)


# .add_button(GP#, Label, Keycode)
# keyb.add_button(3,'ECM','E')

keyb.run()



# type: ignore # Provide a way to enable USB storage after its been disabled
# storage_unlock_pin = board.GP4
# # this is pseudocode:
# if storage_unlock_pin is True
#	import os
#	os.remove('boot.py')
#	os.hardboot()
