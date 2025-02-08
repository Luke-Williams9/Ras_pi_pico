"""
Raspberry Pi Pico GPIO Controller Module

This module provides classes for controlling GPIO pins on a Raspberry Pi Pico,
specifically designed for creating custom input devices like macro keypads and
rotary encoders. It supports both physical pin numbers and GPIO numbers for
flexible pin configuration.

Key Features:
- Button support with short and long press detection
- Rotary encoder support with multiple modes (scroll, zoom, volume)
- GPIO diagnostic tools for testing and debugging
- Edit mode support for safe USB drive access

Classes:
    ButtonController: Main controller for buttons and encoders
    gpio_diag: Diagnostic tool for monitoring GPIO pin states

Dependencies:
    - CircuitPython
    - Adafruit HID library
    - board
    - digitalio
    - rotaryio
    - usb_hid
"""

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
from env import EDIT_MODE_PIN

class ButtonController:
    """Main controller for GPIO-based input devices.
    
    This class manages button and rotary encoder inputs, converting them into
    keyboard shortcuts, mouse movements, or custom macro actions. It supports
    both physical pin numbers and GPIO numbers for flexible configuration.
    
    Features:
        - Button input with short and long press detection
        - Rotary encoder support with multiple modes:
            * Horizontal/vertical scrolling
            * Zoom control
            * Volume control
            * Custom key mappings
            * Custom macro functions
        - Flexible pin configuration using either physical pins or GPIO numbers
        - Edit mode protection to prevent accidental pin usage
    
    Example:
        >>> controller = ButtonController()
        >>> # Add a button that sends 'A' on short press
        >>> controller.add_button("key_a", gpio=15, kbd_key="A")
        >>> # Add an encoder for horizontal scrolling
        >>> controller.add_encoder("scroll", gpio_a=16, gpio_b=17, scroll_mode="horizontal")
        >>> controller.run()
    """
    class PicoGPIO:
        """Helper class for Raspberry Pi Pico GPIO pin mapping.
        
        Provides bidirectional mapping between physical pin numbers (1-40) and
        GPIO numbers (0-28), as well as conversion to board.GP* objects.
        
        The Raspberry Pi Pico has 40 physical pins, but not all are GPIO pins.
        This class maintains the mapping and provides convenient methods to
        convert between different pin numbering systems.
        """
        
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

    def _check_edit_mode_pin(self, board_gpio):
        """Check if the given GPIO pin is the EDIT_MODE_PIN.
        
        Args:
            board_gpio: The board.GP* pin object to check
            
        Raises:
            ValueError: If the pin is the EDIT_MODE_PIN
        """
        if board_gpio == EDIT_MODE_PIN:
            raise ValueError('Cannot use EDIT_MODE_PIN for a button or encoder')

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

    def add_button(self, label, pin=None, gpio=None, kbd_key=None, long_press_threshold=None, macro_short=None, macro_long=None):
        """Add a button to the controller.
        
        Args:
            label (str): Label for the button
            pin (int, optional): Physical pin number (1-40)
            gpio (int, optional): GPIO number (0-28)
            kbd_key (str, optional): Key to press when button is pressed
            long_press_threshold (float, optional): Time in seconds for long press
            macro_short (callable, optional): Function to call on short press
            macro_long (callable, optional): Function to call on long press
            
        Raises:
            ValueError: If pin configuration is invalid or if using EDIT_MODE_PIN
        """
        print('------------')
        print(label)
        print(kbd_key)
        print(macro_short)
        
        # Basic definition error handling
        if kbd_key is None and macro_short is None:
            raise ValueError('Must specify either kbd_key or macro_short')
        if kbd_key is not None and macro_short is not None:
            raise ValueError('Must specify only kbd_key or macro_short')
        if pin is None and gpio is None:
            raise ValueError('Must specify either pin or gpio')
        if pin is not None and gpio is not None:
            raise ValueError('Must specify only pin or gpio')    
        
        # Normalize pin definition
        gpio_number = self._get_gpio_number(pin=pin, gpio=gpio)
        board_gpio = self.gpio.get_board_pin(gpio_number)
        
        # Check if pin is EDIT_MODE_PIN
        self._check_edit_mode_pin(board_gpio)

        button = digitalio.DigitalInOut(board_gpio)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.DOWN
        
        self.buttons[label] = {
            'pin': button,
            'state': False,
            'last_change': time.monotonic(),
            'kbd_key': getattr(Keycode, kbd_key) if kbd_key else None,
            'long_press_threshold': long_press_threshold,
            'macro_short': macro_short,
            'macro_long': macro_long
        }

    def add_encoder(self, label=None, pin_a=None, pin_b=None, gpio_a=None, gpio_b=None,
                   clockwise_key=None, counterclockwise_key=None, 
                   clockwise_macro=None, counterclockwise_macro=None,
                   scroll_mode=None, modifier_key=None):
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
            ValueError: If pin configuration is invalid or if using EDIT_MODE_PIN
        """
        if not label:
            label = f"encoder_{len(self.encoders)}"
            
        # Basic definition error handling
        if clockwise_key is None and clockwise_macro is None and scroll_mode is None:
            raise ValueError('Must specify either clockwise_key, clockwise_macro, or scroll_mode')
        if clockwise_key is not None and clockwise_macro is not None:
            raise ValueError('Must specify only clockwise_key or clockwise_macro')
        if counterclockwise_key is not None and counterclockwise_macro is not None:
            raise ValueError('Must specify only counterclockwise_key or counterclockwise_macro')
            
        # Get GPIO numbers and check pins
        gpio_number_a = self._get_gpio_number(pin=pin_a, gpio=gpio_a)
        gpio_number_b = self._get_gpio_number(pin=pin_b, gpio=gpio_b)
        
        # Check if either pin is EDIT_MODE_PIN
        board_gpio_a = self.gpio.get_board_pin(gpio_number_a)
        board_gpio_b = self.gpio.get_board_pin(gpio_number_b)
        self._check_edit_mode_pin(board_gpio_a)
        self._check_edit_mode_pin(board_gpio_b)
            
        # Create the encoder using rotaryio
        encoder = rotaryio.IncrementalEncoder(board_gpio_a, board_gpio_b)
        
        # Convert modifier key string to Keycode if provided
        modifier = None
        if modifier_key:
            modifier = getattr(Keycode, modifier_key.upper())
        
        self.encoders[label] = {
            'encoder': encoder,
            'last_position': None,
            'clockwise_key': getattr(Keycode, clockwise_key) if clockwise_key else None,
            'counterclockwise_key': getattr(Keycode, counterclockwise_key) if counterclockwise_key else None,
            'clockwise_macro': clockwise_macro,
            'counterclockwise_macro': counterclockwise_macro,
            'scroll_mode': scroll_mode,
            'modifier_key': modifier
        }

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
        
        This method is called by the main loop to process button state changes.
        It handles both keyboard keys and macro functions, with support for
        long press detection.
        
        Args:
            label (str): Label of the button being handled
            button_config (dict): Configuration dictionary containing:
                - pin: DigitalInOut object for the button
                - state: Current button state
                - last_change: Time of last state change
                - kbd_key: Keycode to send (if any)
                - long_press_threshold: Time for long press (if any)
                - macro_short: Function to call on short press
                - macro_long: Function to call on long press
        """
        current_state = button_config['pin'].value
        current_time = time.monotonic()
        
        # Button state changed
        if current_state != button_config['state']:
            # Button pressed
            if current_state:
                # Reset the last change time
                button_config['last_change'] = current_time
                
                # If it's a keyboard key, press it
                if button_config['kbd_key']:
                    self.keyboard.press(button_config['kbd_key'])
                # If it's a short press macro, execute it
                elif button_config['macro_short']:
                    button_config['macro_short']()
            
            # Button released
            else:
                # If it's a keyboard key, release it
                if button_config['kbd_key']:
                    self.keyboard.release(button_config['kbd_key'])
                # If it has a long press threshold and macro
                elif (button_config['long_press_threshold'] and 
                      button_config['macro_long'] and 
                      current_time - button_config['last_change'] >= button_config['long_press_threshold']):
                    # Execute long press macro
                    button_config['macro_long']()
                # If it has a short press macro and we're under the long press threshold
                elif button_config['macro_short'] and (
                    not button_config['long_press_threshold'] or 
                    current_time - button_config['last_change'] < button_config['long_press_threshold']
                ):
                    # Execute short press macro
                    button_config['macro_short']()
            
            # Update state
            button_config['state'] = current_state

    def run(self):
        """Main loop to handle all button and encoder events.
        
        This method runs indefinitely, processing all configured buttons and
        encoders. It handles:
        - Button press/release detection
        - Long press timing
        - Encoder rotation
        - Key press/release events
        - Macro execution
        
        The loop includes a small delay to prevent excessive CPU usage.
        """
        while True:
            # Handle buttons
            for label, button_config in self.buttons.items():
                self._handle_key(label, button_config)
                
            # Handle encoders
            for label, encoder_config in self.encoders.items():
                self._handle_encoder(label, encoder_config)
                
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)

class gpio_diag:
    """Diagnostic tool for monitoring GPIO pin state changes.
    
    This class provides a simple interface for monitoring the state of all
    GPIO pins on the Raspberry Pi Pico. It's particularly useful for:
    - Testing button and encoder connections
    - Debugging pin configuration issues
    - Verifying pull-up/pull-down behavior
    
    Example:
        >>> diag = gpio_diag()
        >>> diag.monitor_gpio()  # Starts monitoring all GPIO pins
    """
    
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
                io.pull = digitalio.Pull.DOWN
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
