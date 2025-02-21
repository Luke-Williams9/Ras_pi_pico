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

    def __init__(self):
        self.buttons = {}
        self.keyboard = Keyboard(usb_hid.devices)
        self.mouse = Mouse(usb_hid.devices)
        self.cc = ConsumerControl(usb_hid.devices)  # For media controls

    def _pinObj(self, gpio):
        """Returns a board.GP* pin object for the given GPIO number"""
        if gpio == PRODUCTION_MODE_PIN:
            raise ValueError(f'Cannot use PRODUCTION_MODE_PIN {PRODUCTION_MODE_PIN} for a button or encoder')
        return getattr(board, f'GP{gpio}')
    
    def _btnObj(self, gpio):
        """Returns a button object"""
        pin_obj = self._pinObj(gpio)
        btn = digitalio.DigitalInOut(pin_obj)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = SWITCH_MODE
        return btn

    def _ledObj(self, gpio):
        """Returns an LED or on/off output object"""
        pin_obj = self._pinObj(gpio)
        led = digitalio.DigitalInOut(pin_obj)
        led.direction = digitalio.Direction.OUTPUT
        led.pull = SWITCH_MODE
        return led

    def add_button(self, label, gpio, kbd_key=None, macro_press=None, macro_long=None, macro_release=None, long_press_threshold=None):
        """Add a button to the controller.
        
        Args:   
            label (str): Label for the button
            gpio (int, optional): GPIO number (0-28)
            kbd_key (str, optional): Key to press when button is pressed
            long_press_threshold (float, optional): Time in seconds for long press
            macro_press (callable, optional): Function to call on short press
            macro_long (callable, optional): Function to call on long press
            macro_release (callable, optional): Function to call on button release
            
        Raises:
            ValueError: If pin configuration is invalid or if using PRODUCTION_MODE_PIN
        """
        
        # print('---------------------------------')
        # print(f"Add Button - {label}")
        button = self._btnObj(gpio)
        btn = {
            'pin': button,
            'pressed': False,
            'last_change': time.monotonic(),
            'kbd_key': getattr(Keycode, kbd_key) if kbd_key else None,
            'long_press_threshold': long_press_threshold,
            'macro_press': macro_press,
            'macro_long': macro_long,
            'macro_release': macro_release,
            'macro_long_ran': False
        }
        
        # print(f"GPIO{gpio}")
        if btn['kbd_key'] is None and btn['macro_press'] is None:
            raise ValueError('Must specify either kbd_key or macro_press/macro_long/macro_release')
        if btn['kbd_key'] is not None and (btn['macro_press'] is not None or btn['long_press_threshold'] is not None or btn['macro_release'] is not None):
            raise ValueError('For advanced usage, use macro_press/macro_long/macro_release instead of kbd_key')
        self.buttons[label] = btn      
    

    def h_scroll(self, dir):
        mod_key = Keycode.SHIFT
        self.keyboard.press(mod_key)
        time.sleep(.0001)
        self.mouse.move(wheel=dir)
        time.sleep(.0001)
        self.keyboard.release(mod_key)

    def add_encoder(self, gpio_a, gpio_b, gpio_button):
        # print('---------------------------------')
        # print(f"Add encoder")    
        self.encoder = rotaryio.IncrementalEncoder(self._pinObj(gpio_a), self._pinObj(gpio_b))
        self.enc_last_position = None
        self.enc_mode = 0 # gpio_button switches between modes 0 and 1
        self.enc_actions = [
            {
                'label': "Horizontal Scroll",
                'macro_cw': lambda: self.h_scroll(1),
                'macro_ccw': lambda: self.h_scroll(-1),
                'gpio_led': None,
                'reverse': False
            },
            {
                'label': "Zoom",
                'macro_cw': lambda: self.combo_press(Keycode.COMMAND, 'EQUALS'),
                'macro_ccw': lambda: self.combo_press(Keycode.COMMAND, 'MINUS'),
                'gpio_led': None,
                'reverse': False
            }
        ]
        # print(f"GPIO_A: {gpio_a}, GPIO_B: {gpio_b}")
        if gpio_button:
            self.enc_btn = self._btnObj(gpio_button)
            # print("Button: {gpio_button}")
        else:
            self.enc_btn = None
        self.enc_btn_pressed = False
        
    def combo_press(self, combo, key, t=.001):
        k = getattr(Keycode, key)
        # Ensure combo is a tuple even if a single key is passed
        if not isinstance(combo, (list, tuple)):
            combo = (combo,)
        self.keyboard.press(*combo, k)
        time.sleep(t)
        self.keyboard.release(*combo, k)
    
          
    def _handle_encoder(self, t=.001):
        if not self.encoder:
            return
        if self.enc_last_position is None:
            self.enc_last_position = self.encoder.position
            return
        if self.enc_btn is not None:
            current_state = self.enc_btn.value
            if SWITCH_MODE == digitalio.Pull.UP:
                current_state = not current_state
            if current_state == True and self.enc_btn_pressed == False:
                # encoder button pressed
                if self.enc_mode == 0:
                    self.enc_mode = 1
                else:
                    self.enc_mode = 0
                self.enc_btn_pressed = True
                # print(f"encoder mode change to {self.enc_actions[self.enc_mode]['label']}")
        if current_state == False:
            self.enc_btn_pressed = False
        logline = f"Encoder {self.encoder.position}"
        if self.encoder.position != self.enc_last_position:
            # Calculate number of steps moved
            steps = self.encoder.position - (self.enc_last_position or 0)
            action = self.enc_actions[self.enc_mode]
            if action['reverse'] is True:
                steps = steps * -1
            # print(f"macro_cw type: {type(action['macro_cw'])}, macro_ccw type: {type(action['macro_ccw'])}")
            if steps < 0:
                # CounterClockwise
                logline = f"{logline} CCW"
                if not TEST_MODE:
                    # print(steps)                
                    action['macro_ccw']()
                    time.sleep(.002)
            else:
                # Clockwise
                logline = f"{logline} CW"
                if not TEST_MODE:
                    # print(steps)                
                    # print(f"Before calling macro_cw: {action['macro_cw']}")
                    action['macro_cw']()
                    # print(f"After calling macro_cw: {action['macro_cw']}")
                    time.sleep(.002)
            logline = f"{logline} {steps} steps"
            time.sleep(.0002)
            # print(logline)
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
                # print(f"{logline} pressed")
                # start the buttons timer
                btn_obj['last_change'] = current_time
                
                # If it's a keyboard key, press it
                if btn_obj['kbd_key']:
                    # print(f"{logline} kbd_key: {btn_obj['kbd_key']} pressed")
                    if not TEST_MODE:
                        self.keyboard.press(btn_obj['kbd_key'])
                # If it's a short press macro, execute it
                if btn_obj['macro_press']:
                    # print(f"{logline} macro_press executed")
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
                    # print(f"{logline} macro_release executed")
                    if not TEST_MODE:
                        btn_obj['macro_release']()
                # print(f"{logline} kbd_key: {btn_obj['kbd_key']} released")
                btn_obj['macro_long_ran'] = False
            # Update state
            btn_obj['pressed'] = current_state
        # Execute long press macro if threshold is exceeded
        if btn_obj['pressed'] is True and btn_obj['macro_long'] is not None and btn_obj['macro_long_ran'] is False and current_time - btn_obj['last_change'] >= btn_obj['long_press_threshold']:
            # print(f"{logline} macro_long executed")
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
            time.sleep(0.0002)

