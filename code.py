import time
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
import board
import digitalio
import gc

def macro_function():
    print("MACRO")
    
# GPIOpin, label, short_key, long_thresh, long_callback
button_map = [
    (2, "Button 1", "A", 2.0, macro_function),
    (3, "Button 2", "B", 1.5, lambda: print("Button 2 long press!")),
    (4, "Button 3", "C", None, None),  # Short press only
    (5, "Button 4", "D", 2.0, lambda: print("Button 4 long press!")),
    (6, "Button 5", "E", None, None),  # Short press only
    (7, "Button 6", "F", 2.0, lambda: print("Button 6 long press!")),
    (8, "Button 7", "G", 1.0, macro_function),
    (9, "Button 8", "H", None, None),
    (10, "Button 9", "I", 3.0, lambda: print("Button 9 long press!")),
    (11, "Button 10", "J", 2.5, macro_function),
]




class ButtonController:
    def __init__(self):
        self.buttons = {}
        self.keyboard = Keyboard(usb_hid.devices)

    def add_button(self, pin_number, label, short_press_key=None, long_press_threshold=None, long_press_callback=None):
        pin = getattr(board, f"GP{pin_number}")
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.DOWN
        self.buttons[label] = {
            'button': button,
            'short_press_key': getattr(Keycode, short_press_key) if short_press_key else None,
            'long_press_threshold': long_press_threshold,
            'long_press_callback': long_press_callback,
            'pressed': False,
            'press_time': None,
        }

    def run(self):
        while True:
            for label, info in self.buttons.items():
                button = info['button']
                short_press_key = info['short_press_key']
                long_press_threshold = info['long_press_threshold']
                long_press_callback = info['long_press_callback']

                try:
                    # Button pressed
                    if button.value and not info['pressed']:
                        info['pressed'] = True
                        info['press_time'] = time.monotonic()

                        # Handle short press immediately
                        if short_press_key:
                            self.keyboard.press(short_press_key)

                    # Button still pressed (check for long press)
                    elif button.value and info['pressed']:
                        if long_press_threshold and (time.monotonic() - info['press_time']) > long_press_threshold:
                            if long_press_callback:
                                long_press_callback()
                                # Reset press time to prevent multiple long press triggers
                                info['press_time'] = time.monotonic()

                    # Button released
                    elif not button.value and info['pressed']:
                        info['pressed'] = False

                        # Handle short press release
                        if short_press_key:
                            self.keyboard.release(short_press_key)

                        # Reset press time
                        info['press_time'] = None

                except ValueError as e:
                    print(f"Error: {e}")

            time.sleep(0.01)




class gpio_diag:
    def __init__(self):
        self.buttons = {}
        self.keyboard = None  # Set up only if needed for HID
    
    def monitor_gpio(self):
        # Create a dictionary to track the last known state of each pin
        pin_states = {}
        gpio_pins = [getattr(board, f"GP{i}") for i in range(0, 29) if hasattr(board, f"GP{i}")]
        
        # Initialize all GPIO pins for input
        pins = {}
        for pin in gpio_pins:
            io = digitalio.DigitalInOut(pin)
            io.direction = digitalio.Direction.INPUT
            io.pull = digitalio.Pull.DOWN
            pins[pin] = io
            pin_states[pin] = io.value
        
        print("Monitoring GPIO pins... (Press Ctrl+C to stop)")
        try:
            while True:
                for pin, io in pins.items():
                    current_state = io.value
                    if current_state != pin_states[pin]:  # State changed
                        state_str = "HIGH" if current_state else "LOW"
                        print(f"Pin {pin}: {state_str}")
                        pin_states[pin] = current_state  # Update state
                time.sleep(0.01)  # Avoid hogging the CPU
        except KeyboardInterrupt:
            print("Monitoring stopped.")

# Usage example
keyb = gpio_diag()
keyb.monitor_gpio()









# Initialize and load button definitions
# keyb = ButtonController()
# for pin, label, short_key, long_thresh, long_callback in button_map:
#     keyb.add_button(pin, label, short_key, long_thresh, long_callback)

def macro_freemem():
    print("Free memory:", gc.mem_free())


# Example usage
def macro_one():
    print("Long press action triggered!")

# Initialize ButtonController
# keyb = ButtonController()

# Add all buttons from the map
# for pin, label, key in button_map:
#    keyb.add_button(pin, label, key)


# keyb.run()




# type: ignore # Provide a way to enable USB storage after its been disabled
# storage_unlock_pin = board.GP4
# # this is pseudocode:
# if storage_unlock_pin is True
#	import os
#	os.remove('boot.py')
#	os.hardboot()
