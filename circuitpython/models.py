import time
import board
import digitalio
import usb_hid
import rotaryio
import supervisor
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from env import PRODUCTION_MODE_PIN, SWITCH_MODE, TEST_MODE

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
            a[key] = value  # Create a local variable with the name of the key
        print('---------------------------------')
        print(f"Add Button - {label}")
        print(f"kwargs: {kwargs}")
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
        
        print(f"GPIO{gpio_number}")
        # for key, value in btn.items():
        #     print(f"{key}: {value}")
        # Error handling after defining btn, so we don't have to a.get() everything
        if btn['kbd_key'] is None and btn['macro_press'] is None:
            raise ValueError('Must specify either kbd_key or macro_press/macro_long/macro_release')
        if btn['kbd_key'] is not None and (btn['macro_press'] is not None or btn['long_press_threshold'] is not None or btn['macro_release'] is not None):
            raise ValueError('For advanced usage, use macro_press/macro_long/macro_release instead of kbd_key')
        self.buttons[label] = btn

    def add_encoder(self, gpio_a, gpio_b, gpio_button, modes):
        print('---------------------------------')
        print(f"Add encoder")    
        
        self._check_production_mode_pin(gpio_a)
        self._check_production_mode_pin(gpio_b)
        
        self.encoder = rotaryio.IncrementalEncoder(self.gpio.get_board_pin(gpio_a), self.gpio.get_board_pin(gpio_b))
        self.enc_last_position = None
        self.enc_modes = modes
        self.enc_mode = modes[0]
         
        self.enc_btn = digitalio.DigitalInOut(self.gpio.get_board_pin(gpio_button))
        self.enc_btn.direction = digitalio.Direction.INPUT
        self.enc_btn.pull = SWITCH_MODE
        self.enc_btn_pressed = False
        print(f"GPIO_A: {gpio_a}, GPIO_B: {gpio_b}")
        print(f"Modes: {modes}")        
        
        
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

    def _handle_encoder(self):
        if self.enc_last_position is None:
            self.enc_last_position = self.encoder.position
            return
        current_state = self.enc_btn.value
        if SWITCH_MODE == digitalio.Pull.UP:
            current_state = not current_state
        if current_state == True and self.enc_btn_pressed == False:
            # encoder button pressed
            if self.enc_mode == self.enc_modes[0]:
                self.enc_mode = self.enc_modes[1]
            else:
                self.enc_mode = self.enc_modes[0]
            self.enc_btn_pressed = True
            print(f"encoder mode change to {self.enc_mode}")
        if current_state == False:
            self.enc_btn_pressed = False
        logline = f"Encoder {self.encoder.position}"
        
        if self.encoder.position != self.enc_last_position:
            # Calculate number of steps moved
            steps = self.encoder.position - (self.enc_last_position or 0)
            
            if self.enc_mode == 'horizontal':
                logline = f"{logline} horizontal scroll"
                # Horizontal scroll with configurable modifier (default: SHIFT)
                mod_key = Keycode.SHIFT
                if steps > 0:
                    # scroll left
                    logline = f"{logline} left"
                    if not TEST_MODE:
                        self.keyboard.press(mod_key)
                        self.mouse.move(wheel=-1)
                        self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between scrolls
                else:
                    # scroll right
                    logline = f"{logline} right"
                    if not TEST_MODE:
                        self.keyboard.press(mod_key)
                        self.mouse.move(wheel=1)
                        self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between scrolls
            elif self.enc_mode == 'zoom':
                # Zoom with configurable modifier (default: CONTROL)
                mod_key = Keycode.CONTROL
                logline = f"{logline} zoom"
                if steps < 0:
                    # Zoom in
                    logline = f"{logline} in"
                    if not TEST_MODE:
                        self.keyboard.press(mod_key)
                        self.mouse.move(wheel=1)
                        self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between zooms
                else:
                    # Zoom out
                    logline = f"{logline} out"
                    if not TEST_MODE:
                        self.keyboard.press(mod_key)
                        self.mouse.move(wheel=-1)
                        self.keyboard.release(mod_key)
                    time.sleep(0.01)  # Small delay between zooms
            elif self.enc_mode == 'vertical':
                # Vertical scroll (no modifier needed)
                logline = f"{logline} vertical scroll"
                if steps > 0:
                    # scroll up
                    logline = f"{logline} up"
                    if not TEST_MODE:
                        self.mouse.move(wheel=1)
                    time.sleep(0.01)  # Small delay between scrolls
                else:
                    # scroll down
                    logline = f"{logline} down"
                    if not TEST_MODE:
                        self.mouse.move(wheel=-1)
                    time.sleep(0.01)  # Small delay between scrolls
            elif self.enc_mode == 'volume':
                # Volume control
                logline = f"{logline} volume"
                if steps > 0:
                    # Volume up
                    logline = f"{logline} up"
                    if not TEST_MODE:
                        self.cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                    time.sleep(0.05)  # Slightly longer delay for volume changes
                else:
                    # Volume down
                    logline = f"{logline} down"
                    if not TEST_MODE:
                        self.cc.send(ConsumerControlCode.VOLUME_DECREMENT)
                    time.sleep(0.05)  # Slightly longer delay for volume changes
            else:
                logline = f"{logline} key"
#                 # Regular key press handling
#                 if steps > 0 and enc_obj['clockwise_key']:
#                     logline = f"{logline} {enc_obj['clockwise_key']}"
#                     if not TEST_MODE:
#                         self.keyboard.press(enc_obj['clockwise_key'])
#                         time.sleep(0.03)  # Delay between key press and release
#                         self.keyboard.release(enc_obj['clockwise_key'])
#                     time.sleep(0.02)  # Delay before next possible key press
#                 elif steps < 0 and enc_obj['counterclockwise_key']:
#                     logline = f"{logline} {enc_obj['counterclockwise_key']}"
#                     if not TEST_MODE:
#                         self.keyboard.press(enc_obj['counterclockwise_key'])
#                         time.sleep(0.03)  # Delay between key press and release
#                         self.keyboard.release(enc_obj['counterclockwise_key'])
#                     time.sleep(0.02)  # Delay before next possible key press
#                 elif steps > 0 and enc_obj['clockwise_macro']:
#                     logline = f"{logline} {enc_obj['clockwise_macro']}"
#                     if not TEST_MODE:
#                         enc_obj['clockwise_macro']()
#                     time.sleep(0.05)  # Delay after macro execution
#                 elif steps < 0 and enc_obj['counterclockwise_macro']:
#                     logline = f"{logline} {enc_obj['counterclockwise_macro']}"
#                     if not TEST_MODE:
#                         enc_obj['counterclockwise_macro']()
#                     time.sleep(0.05)  # Delay after macro execution
            print(logline)
            self.enc_last_position = self.encoder.position

    def _handle_key(self, label, btn_obj):
        """Handle key press/release events and execute corresponding actions.
        
        Args:
            label (str): Label of the button being handled
            btn_obj (dict): Configuration for the button including pin, state, etc.
        """
        current_state = btn_obj['pin'].value
        current_time = time.monotonic()
        if SWITCH_MODE == digitalio.Pull.UP:
            current_state = not current_state
        # Has the button state changed?
        logline = f"Button {label} - GPIO{btn_obj['pin'].value}"
        
        
        if current_state != btn_obj['pressed']:
            # Button pressed
            if current_state:
                print(f"{logline} pressed")
                # start the buttons timer
                btn_obj['last_change'] = current_time
                
                # If it's a keyboard key, press it
                if btn_obj['kbd_key']:
                    print(f"{logline} kbd_key: {btn_obj['kbd_key']} pressed")
                    if not TEST_MODE:
                        self.keyboard.press(btn_obj['kbd_key'])
                # If it's a short press macro, execute it
                if btn_obj['macro_press']:
                    print(f"{logline} macro_press executed")
                    if not TEST_MODE:
                        btn_obj['macro_press']()
            # Button released
            else:
                # If it's a keyboard key, release it
                if btn_obj['kbd_key']:
                    if not TEST_MODE:
                        self.keyboard.release(btn_obj['kbd_key'])
                # If it has a release macro, execute it
                if btn_obj['macro_release']:
                    print(f"{logline} macro_release executed")
                    if not TEST_MODE:
                        btn_obj['macro_release']()
                print(f"{logline} kbd_key: {btn_obj['kbd_key']} released")
                btn_obj['macro_long_ran'] = False
            # Update state
            btn_obj['pressed'] = current_state
        # Execute long press macro if threshold is exceeded
        if btn_obj['pressed'] is True and btn_obj['macro_long'] is not None and btn_obj['macro_long_ran'] is False and current_time - btn_obj['last_change'] >= btn_obj['long_press_threshold']:
            print(f"{logline} macro_long executed")
            if not TEST_MODE:
                btn_obj['macro_long']()  
            btn_obj['macro_long_ran'] = True
    def run(self):
        """Main loop to handle all button and encoder events."""
        while True:
            if supervisor.runtime.serial_bytes_available:  # Check if Ctrl+C was sent
                break  # Exit the loop and stop the program
            # Handle buttons
            for label, btn_obj in self.buttons.items():
                self._handle_key(label, btn_obj)
            self._handle_encoder()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.05)

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
