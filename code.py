import time
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
import board
import digitalio
import gc





class ButtonController:
    def __init__(self):
        self.buttons = {}
        self.keyboard = Keyboard(usb_hid.devices)

    def add_button(self, pin_number, label, kbd_key=None, long_press_threshold=None, macro_short=None, macro_long=None):
        if kbd_key is None and macro_short is None:
            raise ValueError('Must specify either kby_key or macro_short')
        if kbd_key is not None and macro_short is not None:
            raise ValueError('Must specify only kby_key or macro_short')
        pin = getattr(board, f"GP{pin_number}")
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.DOWN
        # p is the contents of this
        self.buttons[label] = {
            'button': button,
            'kbd_key': getattr(Keycode, kbd_key) if kbd_key else None,
            'long_press_threshold': long_press_threshold,
            'macro_short': macro_short,
            'macro_long': macro_long,
            'pressed': False,
            'press_time': None,
        }
    def raw_press(self, *keys):
        self.keyboard.press(*keys)

    def raw_release(self, *keys):
        self.keyboard.release(*keys)

    
    def run(self):
        while True:
            for label, p in self.buttons.items():
                try:
                    # Button pressed
                    if p['button'].value and not p['pressed']:
                        p['pressed'] = True
                        p['press_time'] = time.monotonic()

                        # Handle short press immediately

                        if p['kbd_key']:
                            self.keyboard.press(p['kbd_key'])
                        else:
                            p['macro_short']()

                    # Button still pressed (check for long press)
                    elif p['button'].value and p['pressed']:
                        if p['long_press_threshold'] and (time.monotonic() - p['press_time']) > p['long_press_threshold']:
                            if p['macro_long']:
                                p['macro_long']()
                                p['press_time'] = time.monotonic() 

                    # Button released
                    elif not p['button'].value and p['pressed']:
                        p['pressed'] = False
                        if p['kbd_key']:
                            self.keyboard.release(p['kbd_key'])
                        p['press_time'] = None

                except ValueError as e:
                    print(f"Error: {e}")

            time.sleep(0.02)




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


# Initialize and load button definitions
keyb = ButtonController()
def macro_freemem():
    print("Free memory:", gc.mem_free())

button_map = {
    "Button 1": {
        "pin": 14,
        "kbd_key": "A",
        "long_press_threshold": 2,
        "macro_long": lambda: print("Button 1 long press triggered!"),
    },
    "Button 2": {
        "pin": 15,
        "macro_short": lambda: print("Button 2 short macro triggered!"),
        "long_press_threshold": 1,
        "macro_long": lambda: print("Free memory:", gc.mem_free()),
    },
    "Button 3": {
        "pin": 5,
        "kbd_key": "B",
    },
    "Button 4": {
        "pin": 3,
        "macro_short": lambda: print("Button 4 short macro triggered!"),
    },
    "Button 5": {
        "pin": 16,
        "kbd_key": "C",
        "long_press_threshold": 3,
        "macro_long": lambda: print("Button 5 long macro triggered!"),
    },
    "Button 6": {
        "pin": 2,
        "macro_short": lambda: print("Button 6 short macro triggered!"),
        "long_press_threshold": 2,
        "macro_long": lambda: print("Button 6 long macro triggered!"),
    },
    "Button 7": {
        "pin": 0,
        "kbd_key": "D",
    },
    "Button 8": {
        "pin": 9,
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
            keyb.raw_press(Keycode.CONTROL, Keycode.ALT, Keycode.F),
            time.sleep(1),
            keyb.raw_release(Keycode.CONTROL, Keycode.ALT, Keycode.F),
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
