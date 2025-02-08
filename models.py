import time
import board
import digitalio
import usb_hid
import rotaryio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

class ButtonController:
    def __init__(self):
        self.buttons = {}
        self.encoders = {}  # Store encoder configurations
        self.keyboard = Keyboard(usb_hid.devices)

    def add_button(self, pin_number, label, kbd_key=None, long_press_threshold=None, macro_short=None, macro_long=None):
        print('------------')
        print(label)
        print(kbd_key)
        print(macro_short)
        if kbd_key is None and macro_short is None:
            raise ValueError('Must specify either kbd_key or macro_short')
        if kbd_key is not None and macro_short is not None:
            raise ValueError('Must specify only kdy_key or macro_short')
        pin = getattr(board, f"GP{pin_number}")
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.DOWN
        # this is all in p in run()
        self.buttons[label] = {
            'button': button,
            'kbd_key': getattr(Keycode, kbd_key) if kbd_key else None,
            'long_press_threshold': long_press_threshold,
            'macro_short': macro_short,
            'macro_long': macro_long,
            'pressed': False,
            'press_time': None,
        }

    def add_encoder(self, pin_a, pin_b, label=None, 
                   clockwise_key=None, counterclockwise_key=None, 
                   clockwise_macro=None, counterclockwise_macro=None):
        """Add a rotary encoder to the controller.
        
        Args:
            pin_a (int): GPIO pin number for encoder pin A
            pin_b (int): GPIO pin number for encoder pin B
            label (str, optional): Label for the encoder
            clockwise_key (str, optional): Keycode to send on clockwise rotation
            counterclockwise_key (str, optional): Keycode to send on counterclockwise rotation
            clockwise_macro (callable, optional): Function to call on clockwise rotation
            counterclockwise_macro (callable, optional): Function to call on counterclockwise rotation
        """
        if not label:
            label = f"encoder_{len(self.encoders)}"
            
        # Create the encoder using rotaryio
        encoder = rotaryio.IncrementalEncoder(
            getattr(board, f"GP{pin_a}"),
            getattr(board, f"GP{pin_b}")
        )
        
        self.encoders[label] = {
            'encoder': encoder,
            'last_position': None,
            'clockwise_key': getattr(Keycode, clockwise_key) if clockwise_key else None,
            'counterclockwise_key': getattr(Keycode, counterclockwise_key) if counterclockwise_key else None,
            'clockwise_macro': clockwise_macro,
            'counterclockwise_macro': counterclockwise_macro
        }

    def _handle_encoder(self, label, encoder_config):
        """Handle encoder movement detection and actions."""
        position = encoder_config['encoder'].position
        
        if encoder_config['last_position'] is None:
            encoder_config['last_position'] = position
            return
            
        if position != encoder_config['last_position']:
            # Determine direction
            if position > encoder_config['last_position']:
                # Clockwise
                if encoder_config['clockwise_key']:
                    self.keyboard.press(encoder_config['clockwise_key'])
                    self.keyboard.release(encoder_config['clockwise_key'])
                if encoder_config['clockwise_macro']:
                    encoder_config['clockwise_macro']()
            else:
                # Counter-clockwise
                if encoder_config['counterclockwise_key']:
                    self.keyboard.press(encoder_config['counterclockwise_key'])
                    self.keyboard.release(encoder_config['counterclockwise_key'])
                if encoder_config['counterclockwise_macro']:
                    encoder_config['counterclockwise_macro']()
            
            encoder_config['last_position'] = position

    def raw_press(self, *keys):
        self.keyboard.press(*keys)

    def raw_release(self, *keys):
        self.keyboard.release(*keys)
    
    def combo_press(self, combo, key, t=.1):
        print(key)
        print("Keycode in scope:", "Keycode" in globals(), "Keycode" in locals())
        k = getattr(Keycode, key)
        self.raw_press(*combo, k),
        time.sleep(t),
        self.raw_release(*combo, k)

    def run(self):
        while True:
            # Handle buttons
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
            
            # Handle encoders
            for label, encoder in self.encoders.items():
                try:
                    self._handle_encoder(label, encoder)
                except ValueError as e:
                    print(f"Encoder error: {e}")

            time.sleep(0.02)


class gpio_diag:
    def __init__(self):
        self.buttons = {}
        self.encoders = {}  # Store encoder objects
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
        
        # Set up some test encoder pairs
        encoder_pairs = [
            (8, 9),    # Test encoder 1
            (10, 11),  # Test encoder 2
            (12, 13),  # Test encoder 3
            (14, 15)   # Test encoder 4
        ]
        
        # Initialize encoders
        for pin_a, pin_b in encoder_pairs:
            try:
                encoder = rotaryio.IncrementalEncoder(
                    getattr(board, f"GP{pin_a}"),
                    getattr(board, f"GP{pin_b}")
                )
                self.encoders[f"encoder_{pin_a}_{pin_b}"] = {
                    'encoder': encoder,
                    'last_position': encoder.position,
                    'pin_a': pin_a,
                    'pin_b': pin_b
                }
                print(f"Successfully initialized encoder on pins GP{pin_a}/GP{pin_b}")
            except Exception as e:
                print(f"Could not initialize encoder on pins GP{pin_a}/GP{pin_b}: {e}")
        
        print("Monitoring GPIO pins and encoders... (Press Ctrl+C to stop)")
        try:
            while True:
                # Monitor regular GPIO pins
                for pin, io in pins.items():
                    current_state = io.value
                    if current_state != pin_states[pin]:  # State changed
                        state_str = "HIGH" if current_state else "LOW"
                        print(f"Pin {pin}: {state_str}")
                        pin_states[pin] = current_state  # Update state
                
                # Monitor encoders
                for label, enc in self.encoders.items():
                    position = enc['encoder'].position
                    if position != enc['last_position']:
                        direction = "CW" if position > enc['last_position'] else "CCW"
                        print(f"Encoder {label} (GP{enc['pin_a']}/GP{enc['pin_b']}): {direction} movement, position={position}")
                        enc['last_position'] = position
                
                time.sleep(0.01)  # Avoid hogging the CPU
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            # Clean up
            for pin_io in pins.values():
                pin_io.deinit()
            for enc in self.encoders.values():
                enc['encoder'].deinit()


class EC11RotaryEncoder:
    def __init__(self, pin_a, pin_b, pin_button=None):
        """Initialize EC11 rotary encoder with required pins.
        
        Args:
            pin_a (int): GPIO pin number for encoder pin A
            pin_b (int): GPIO pin number for encoder pin B
            pin_button (int, optional): GPIO pin number for push button
        """
        # Set up rotary encoder pins
        self.pin_a = digitalio.DigitalInOut(getattr(board, f"GP{pin_a}"))
        self.pin_b = digitalio.DigitalInOut(getattr(board, f"GP{pin_b}"))
        self.pin_a.direction = digitalio.Direction.INPUT
        self.pin_b.direction = digitalio.Direction.INPUT
        self.pin_a.pull = digitalio.Pull.UP
        self.pin_b.pull = digitalio.Pull.UP
        
        # Set up button if provided
        self.pin_button = None
        if pin_button is not None:
            self.pin_button = digitalio.DigitalInOut(getattr(board, f"GP{pin_button}"))
            self.pin_button.direction = digitalio.Direction.INPUT
            self.pin_button.pull = digitalio.Pull.UP
        
        # State tracking
        self.last_state = (self.pin_a.value, self.pin_b.value)
        self.button_pressed = False
        self.button_press_time = None
        
        # Callback functions
        self.on_clockwise = None
        self.on_counterclockwise = None
        self.on_button_press = None
        self.on_button_release = None
        self.on_button_long_press = None
        self.long_press_threshold = 1.0  # seconds
        
    def set_callbacks(self, clockwise=None, counterclockwise=None, button_press=None, 
                     button_release=None, button_long_press=None, long_press_threshold=1.0):
        """Set callback functions for encoder events.
        
        Args:
            clockwise: Function to call on clockwise rotation
            counterclockwise: Function to call on counterclockwise rotation
            button_press: Function to call on button press
            button_release: Function to call on button release
            button_long_press: Function to call on long button press
            long_press_threshold: Time in seconds to trigger long press
        """
        self.on_clockwise = clockwise
        self.on_counterclockwise = counterclockwise
        self.on_button_press = button_press
        self.on_button_release = button_release
        self.on_button_long_press = button_long_press
        self.long_press_threshold = long_press_threshold
    
    def update(self):
        """Update encoder state and trigger callbacks. Call this in your main loop."""
        # Read current state
        current_state = (self.pin_a.value, self.pin_b.value)
        
        # Detect rotation
        if current_state != self.last_state:
            # State transition table for clockwise rotation
            if self.last_state == (True, True):
                if current_state == (False, True) and self.on_clockwise:
                    self.on_clockwise()
            elif self.last_state == (False, True):
                if current_state == (False, False) and self.on_clockwise:
                    self.on_clockwise()
            elif self.last_state == (False, False):
                if current_state == (True, False) and self.on_counterclockwise:
                    self.on_counterclockwise()
            elif self.last_state == (True, False):
                if current_state == (True, True) and self.on_counterclockwise:
                    self.on_counterclockwise()
            
            self.last_state = current_state
        
        # Handle button if present
        if self.pin_button:
            button_state = not self.pin_button.value  # Active LOW with pull-up
            current_time = time.monotonic()
            
            # Button pressed
            if button_state and not self.button_pressed:
                self.button_pressed = True
                self.button_press_time = current_time
                if self.on_button_press:
                    self.on_button_press()
            
            # Button held
            elif button_state and self.button_pressed:
                if (self.on_button_long_press and self.button_press_time and 
                    current_time - self.button_press_time > self.long_press_threshold):
                    self.on_button_long_press()
                    self.button_press_time = current_time
            
            # Button released
            elif not button_state and self.button_pressed:
                self.button_pressed = False
                if self.on_button_release:
                    self.on_button_release()
                self.button_press_time = None
