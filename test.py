import time
import gc
from adafruit_hid.keycode import Keycode
from models import gpio_diag

keyb = gpio_diag()
keyb.monitor_gpio()