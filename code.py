import time
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
import board
import digitalio



# Provide a way to enable USB storage after its been disabled
storage_unlock_pin = board.GP4
# # this is pseudocode:
# if storage_unlock_pin is True
#	import os
#	os.remove('boot.py')
#	os.hardboot()

btn1_pin = board.GP9


btn1 = digitalio.DigitalInOut(btn1_pin)
btn1.direction = digitalio.Direction.INPUT
btn1.pull = digitalio.Pull.DOWN


keyboard = Keyboard(usb_hid.devices)

while True:
    if btn1.value:
        print('buttonpress')
        keyboard.send(Keycode.ONE)
        time.sleep(0.1)
    time.sleep(0.1)
