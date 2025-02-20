from machine import Pin
import time
#from models import Encoder

from machine import Pin

# encoder_portable.py

# Encoder Support: this version should be portable between MicroPython platforms
# Thanks to Evan Widloski for the adaptation to use the machine module

# Copyright (c) 2017-2022 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file
# https://github.com/peterhinch/micropython-samples/blob/master/encoders/encoder_portable.py


from machine import Pin
import time

class Encoder:
    def __init__(self, pin_x, pin_y, name, scale=1):
        self.scale = scale
        self.name = name
        self.pin_x = Pin(pin_x, Pin.IN, Pin.PULL_UP)
        self.pin_y = Pin(pin_y, Pin.IN, Pin.PULL_UP)
        self._pos = 0
        self._last_x = self.pin_x.value()
        self.update_flag = False  # New flag to process updates outside IRQ

        # Attach interrupts with minimal processing
        self.pin_x.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.x_callback)
        self.pin_y.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.y_callback)

    def x_callback(self, pin):
        """Minimal IRQ handler to avoid MemoryError"""
        self.update_flag = True  # Set flag for processing in main loop

    def y_callback(self, pin):
        """Minimal IRQ handler"""
        self.update_flag = True  # Set flag for processing in main loop

    def process_movement(self):
        """Process encoder movement in the main loop"""
        x = self.pin_x.value()
        if x != self._last_x:  # Change detected
            self._last_x = x
            if self.pin_y.value() != x:  # Clockwise
                self._pos += 1
            else:  # Counterclockwise
                self._pos -= 1
            print(f"{self.name} Position: {self._pos}")  # Safe to print here

# Instantiate encoder with correct GPIOs
enc1 = Encoder(0, 1, "1")
enc2 = Encoder(2, 3, "2")

# Main loop processes movement **outside** the IRQ
while True:
    if enc1.update_flag:
        enc1.process_movement()  # Handle movement outside IRQ
        enc1.update_flag = False  # Reset flag
    if enc2.update_flag:
        enc2.process_movement()  # Handle movement outside IRQ
        enc2.update_flag = False  # Reset flag
    time.sleep(0.001)  # Small delay to prevent CPU overuse



