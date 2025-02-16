import time
import board
import digitalio
import usb_hid
import rotaryio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from env import PRODUCTION_MODE_PIN, SWITCH_MODE

class ButtonController:
    class PicoGPIO:
        """Helper class for Raspberry Pi Pico GPIO pin mapping"""
        
        # Physical pin to GPIO mapping
        PIN_TO_GPIO = {
            1: 0,   # GP0
            2: 1,   # GP1
            4: 2,   # GP2
            5: 3,   # GP3
            6: 4,   # GP4
            7: 5,   # GP5
            9: 6,   # GP6
            10: 7,  # GP7
            11: 8,  # GP8
            12: 9,  # GP9
            14: 10, # GP10
            15: 11, # GP11
            16: 12, # GP12
            17: 13, # GP13
            19: 14, # GP14
            20: 15, # GP15
            21: 16, # GP16
            22: 17, # GP17
            24: 18, # GP18
            25: 19, # GP19
            26: 20, # GP20
            27: 21, # GP21
            29: 22, # GP22
            31: 26, # GP26
            32: 27, # GP27
            34: 28, # GP28
        }
        
        # GPIO to physical pin mapping (reverse of PIN_TO_GPIO)
        GPIO_TO_PIN = {gpio: pin for pin, gpio in PIN_TO_GPIO.items()}
        
        def __init__(self):
            pass
        
        def get_gpio_pin(self, physical_pin):
            """Convert physical pin number to GPIO number"""
            return self.PIN_TO_GPIO.get(physical_pin)
        
        def get_physical_pin(self, gpio):
            """Convert GPIO number to physical pin number"""
            return self.GPIO_TO_PIN.get(gpio)
        
        def get_board_pin(self, gpio):
            """Get the board.GP* pin object for a GPIO number"""
            return getattr(board, f'GP{gpio}')

    def __init__(self):
        # Initialize GPIO helper
        self.gpio = self.PicoGPIO()
        
        # Initialize other components
        self.buttons = {}
        self.encoders = {}  # Store encoder configurations
        self.keyboard = Keyboard(usb_hid.devices)
        self.mouse = Mouse(usb_hid.devices)
        self.cc = ConsumerControl(usb_hid.devices)  # For media controls

    def _check_production_mode_pin(self, board_gpio):
        """Check if the given GPIO pin is the PRODUCTION_MODE_PIN.
        
        Args:
            board_gpio: The board.GP* pin object to check
            
        Raises:
            ValueError: If the pin is the PRODUCTION_MODE_PIN
        """
        if board_gpio == PRODUCTION_MODE_PIN:
            raise ValueError('Cannot use PRODUCTION_MODE_PIN for a button or encoder')

    def _get_gpio_number(self, pin=None, gpio=None):
        """Get GPIO number from either pin or gpio input.
        
        Args:
            pin (int, optional): Physical pin number
            gpio (int, optional): GPIO number
            
        Returns:
            int: The GPIO number
            
        Raises:
            ValueError: If neither or both pin and gpio are specified
        """
        if pin is None and gpio is None:
            raise ValueError('Must specify either pin or gpio')
        if pin is not None and gpio is not None:
            raise ValueError('Must specify only pin or gpio')
            
        if pin is not None:
            return self.gpio.get_gpio_pin(pin)
        return gpio

    #def add_button(self, label, pin=None, gpio=None, kbd_key=None, long_press_threshold=None, macro_press=None, macro_long=None, macro_release=None):
    def add_button(self, label, **kwargs):
        """Add a button to the controller.
        
        Args:   
            label (str): Label for the button
            pin (int, optional): Physical pin number (1-40)
            gpio (int, optional): GPIO number (0-28)
            kbd_key (str, optional): Key to press when button is pressed
            long_press_threshold (float, optional): Time in seconds for long press
            macro_press (callable, optional): Function to call on short press
            macro_long (callable, optional): Function to call on long press
            macro_release (callable, optional): Function to call on button release
            
        Raises:
            ValueError: If pin configuration is invalid or if using PRODUCTION_MODE_PIN
        """
        # unpack the kwargs
        a = {}
        for key, value in kwargs.items():
            print(key)
            a[key] = value  # Create a local variable with the name of the key
        
        # Normalize pin definition

        gpio_number = self._get_gpio_number(pin=a.get('pin'), gpio=a.get('gpio'))
        board_gpio = self.gpio.get_board_pin(gpio_number)
        
        # Check if pin is PRODUCTION_MODE_PIN
        self._check_production_mode_pin(board_gpio)

        button = digitalio.DigitalInOut(board_gpio)
        button.direction = digitalio.Direction.INPUT
        button.pull = SWITCH_MODE
        kk = a.get('kbd_key')
        btn = {
            'pin': button,
            'pressed': False,
            'last_change': time.monotonic(),
            'kbd_key': getattr(Keycode, kk) if kk else None,
            'long_press_threshold': a.get('long_press_threshold'),
            'macro_press': a.get('macro_press'),
            'macro_long': a.get('macro_long'),
            'macro_release': a.get('macro_release'),
            'macro_long_ran': False
        }
        # Error handling after defining btn, so we don't have to a.get() everything
        if btn['kbd_key'] is None and btn['macro_press'] is None:
            raise ValueError('Must specify either kbd_key or macro_press/macro_long/macro_release')
        if btn['kbd_key'] is not None and (btn['macro_press'] is not None or btn['long_press_threshold'] is not None or btn['macro_release'] is not None):
            raise ValueError('For advanced usage, use macro_press/macro_long/macro_release instead of kbd_key')
        self.buttons[label] = btn

    def add_encoder(self, label, **kwargs):
    # def add_encoder(self, label=None, pin_a=None, pin_b=None, gpio_a=None, gpio_b=None,
    #                clockwise_key=None, counterclockwise_key=None, 
    #                clockwise_macro=None, counterclockwise_macro=None,
    #                scroll_mode=None, modifier_key=None):
        """Add a rotary encoder to the controller.
        
        Args:
            label (str, optional): Label for the encoder
            pin_a (int, optional): Physical pin number for encoder pin A
            pin_b (int, optional): Physical pin number for encoder pin B
            gpio_a (int, optional): GPIO number for encoder pin A
            gpio_b (int, optional): GPIO number for encoder pin B
            clockwise_key (str, optional): Keycode to send on clockwise rotation
            counterclockwise_key (str, optional): Keycode to send on counterclockwise rotation
            clockwise_macro (callable, optional): Function to call on clockwise rotation
            counterclockwise_macro (callable, optional): Function to call on counterclockwise rotation
            scroll_mode (str, optional): Type of scrolling: 'horizontal', 'vertical', 'zoom', or 'volume'
            modifier_key (str, optional): Modifier key to use (e.g., 'SHIFT', 'CONTROL', 'COMMAND', 'ALT')
            
        Raises:
            ValueError: If pin configuration is invalid or if using PRODUCTION_MODE_PIN
        """
        # unpack the kwargs
        a = {}
        for key, value in kwargs.items():
            print(key)
            a[key] = value  # Create a local variable with the name of the key
        if not label:
            label = f"encoder_{len(self.encoders)}"
            

        # Get GPIO numbers and check pins
        gpio_number_a = self._get_gpio_number(pin=a.get('pin_a'), gpio=a.get('gpio_a'))
        gpio_number_b = self._get_gpio_number(pin=a.get('pin_b'), gpio=a.get('gpio_b'))
        
        # Check if either pin is PRODUCTION_MODE_PIN
        board_gpio_a = self.gpio.get_board_pin(gpio_number_a)
        board_gpio_b = self.gpio.get_board_pin(gpio_number_b)
        self._check_production_mode_pin(board_gpio_a)
        self._check_production_mode_pin(board_gpio_b)
        kk1 = a.get('clockwise_key')
        kk2 = a.get('counterclockwise_key')
        kkm = a.get('modifier_key')
        enc = {
            'encoder': rotaryio.IncrementalEncoder(board_gpio_a, board_gpio_b),
            'last_position': None,
            'clockwise_key': getattr(Keycode, kk1) if kk1 else None,
            'counterclockwise_key': getattr(Keycode, kk2) if kk2 else None,
            'clockwise_macro': a.get('clockwise_macro'),
            'counterclockwise_macro': a.get('counterclockwise_macro'),
            'scroll_mode': a.get('scroll_mode'),
            'modifier_key': getattr(Keycode, kkm) if kkm else None
        }
        # Basic definition error handling
        if enc['clockwise_key'] is None and enc['clockwise_macro'] is None and enc['scroll_mode'] is None:
            raise ValueError('Must specify either clockwise_key, clockwise_macro, or scroll_mode')
        if enc['clockwise_key'] is not None and enc['clockwise_macro'] is not None:
            raise ValueError('Must specify only clockwise_key or clockwise_macro')
        if enc['counterclockwise_key'] is not None and enc['counterclockwise_macro'] is not None:
            raise ValueError('Must specify only counterclockwise_key or counterclockwise_macro')
        self.encoders[label] = enc
            

    def raw_press(self, *keys):
        self.keyboard.press(*keys)

    def raw_release(self, *keys):
        self.keyboard.release(*keys)
    
    def combo_press(self, combo, key, t=.1):
        print(key)
        print("Keycode in scope:", "Keycode" in globals(), "Keycode" in locals())
        k = getattr(Keycode, key)
        # Ensure combo is a tuple even if a single key is passed
        if not isinstance(combo, (list, tuple)):
            combo = (combo,)
        self.raw_press(*combo, k)
        time.sleep(t)
        self.raw_release(*combo, k)

    def _handle_encoder(self, label, encoder_config):
        """Handle encoder movement detection and actions."""
        position = encoder_config['encoder'].position
        
        if encoder_config['last_position'] is None:
            encoder_config['last_position'] = position
            return
            
        if position != encoder_config['last_position']:
            # Calculate number of steps moved
            steps = position - encoder_config['last_position']
            
            # Get the configured modifier key or use defaults
            modifier = encoder_config['modifier_key']
            
            if encoder_config['scroll_mode'] == 'horizontal':
                # Horizontal scroll with configurable modifier (default: SHIFT)
                mod_key = modifier or Keycode.SHIFT
                if steps > 0:
                    self.keyboard.press(mod_key)
                    self.mouse.move(wheel=-1)
                    self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between scrolls
                else:
                    self.keyboard.press(mod_key)
                    self.mouse.move(wheel=1)
                    self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between scrolls
            elif encoder_config['scroll_mode'] == 'zoom':
                # Zoom with configurable modifier (default: CONTROL)
                mod_key = modifier or Keycode.CONTROL
                if steps > 0:
                    self.keyboard.press(mod_key)
                    self.mouse.move(wheel=1)
                    self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between zooms
                else:
                    self.keyboard.press(mod_key)
                    self.mouse.move(wheel=-1)
                    self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between zooms
            elif encoder_config['scroll_mode'] == 'vertical':
                # Vertical scroll (no modifier needed)
                if steps > 0:
                    self.mouse.move(wheel=1)
                    time.sleep(0.01)  # Small delay between scrolls
                else:
                    self.mouse.move(wheel=-1)
                    time.sleep(0.01)  # Small delay between scrolls
            elif encoder_config['scroll_mode'] == 'volume':
                # Volume control
                if steps > 0:
                    self.cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                    time.sleep(0.05)  # Slightly longer delay for volume changes
                else:
                    self.cc.send(ConsumerControlCode.VOLUME_DECREMENT)
                    time.sleep(0.05)  # Slightly longer delay for volume changes
            else:
                # Regular key press handling
                if steps > 0 and encoder_config['clockwise_key']:
                    self.keyboard.press(encoder_config['clockwise_key'])
                    time.sleep(0.03)  # Delay between key press and release
                    self.keyboard.release(encoder_config['clockwise_key'])
                    time.sleep(0.02)  # Delay before next possible key press
                elif steps < 0 and encoder_config['counterclockwise_key']:
                    self.keyboard.press(encoder_config['counterclockwise_key'])
                    time.sleep(0.03)  # Delay between key press and release
                    self.keyboard.release(encoder_config['counterclockwise_key'])
                    time.sleep(0.02)  # Delay before next possible key press
                elif steps > 0 and encoder_config['clockwise_macro']:
                    encoder_config['clockwise_macro']()
                    time.sleep(0.05)  # Delay after macro execution
                elif steps < 0 and encoder_config['counterclockwise_macro']:
                    encoder_config['counterclockwise_macro']()
                    time.sleep(0.05)  # Delay after macro execution
            
            encoder_config['last_position'] = position

    def _handle_key(self, label, button_config):
        """Handle key press/release events and execute corresponding actions.
        
        Args:
            label (str): Label of the button being handled
            button_config (dict): Configuration for the button including pin, state, etc.
        """
        current_state = button_config['pin'].value
        current_time = time.monotonic()
        if SWITCH_MODE == digitalio.Pull.UP:
            current_state = not current_state
        # Has the button state changed?
        if current_state != button_config['pressed']:
            # Button pressed
            if current_state:
                # start the buttons timer
                button_config['last_change'] = current_time
                
                # If it's a keyboard key, press it
                if button_config['kbd_key']:
                    self.keyboard.press(button_config['kbd_key'])
                # If it's a short press macro, execute it
                if button_config['macro_press']:
                    button_config['macro_press']()
            # Button released
            else:
                # If it's a keyboard key, release it
                if button_config['kbd_key']:
                    self.keyboard.release(button_config['kbd_key'])
                # If it has a release macro, execute it
                if button_config['macro_release']:
                    button_config['macro_release']()
                button_config['macro_long_ran'] = False
            # Update state
            button_config['pressed'] = current_state
        # Execute long press macro if threshold is exceeded
        if button_config['pressed'] is True and button_config['macro_long'] is not None and button_config['macro_long_ran'] is False and current_time - button_config['last_change'] >= button_config['long_press_threshold']:
                button_config['macro_long']()  
                button_config['macro_long_ran'] = True
    def run(self):
        """Main loop to handle all button and encoder events."""
        while True:
            # Handle buttons
            for label, button_config in self.buttons.items():
                self._handle_key(label, button_config)
                
            # Handle encoders
            for label, encoder_config in self.encoders.items():
                self._handle_encoder(label, encoder_config)
                
            # Small delay to prevent excessive CPU usage
            time.sleep(0.02)

class gpio_diag:
    """Diagnostic tool to monitor GPIO pin state changes."""
    
    def __init__(self):
        # Initialize GPIO helper
        self.gpio = ButtonController.PicoGPIO()
        
    def monitor_gpio(self):
        """Monitor all GPIO pins for state changes."""
        # Create a dictionary to track the last known state of each pin
        pin_states = {}
        pins = {}
        
        print("\nInitializing GPIO pins for monitoring...")
        
        # Initialize all GPIO pins (0-28) for input with pull-down
        for gpio_num in range(29):  # GPIO0 to GPIO28
            try:
                pin = self.gpio.get_board_pin(gpio_num)
                io = digitalio.DigitalInOut(pin)
                io.direction = digitalio.Direction.INPUT
                io.pull = SWITCH_MODE
                pins[gpio_num] = io
                pin_states[gpio_num] = False
            except Exception as e:
                print(f"Failed to initialize GPIO {gpio_num}")
        
        print("\nMonitoring GPIO pins. Press Ctrl+C to exit...")
        
        try:
            while True:
                # Check all pins for state changes
                for gpio_num, io in pins.items():
                    current_state = io.value
                    if current_state != pin_states[gpio_num]:
                        state_str = "HIGH" if current_state else "LOW"
                        print(f"GPIO {gpio_num}: {state_str}")
                        pin_states[gpio_num] = current_state
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        finally:
            # Clean up
            for io in pins.values():
                io.deinit()
            print("GPIO pins cleaned up.")
