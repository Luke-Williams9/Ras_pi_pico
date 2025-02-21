import time
import gc
from adafruit_hid.keycode import Keycode

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
                pin = self._pinObj(gpio_num)
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

keyb = gpio_diag()
keyb.monitor_gpio()