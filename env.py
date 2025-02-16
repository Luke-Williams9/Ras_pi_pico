import board, digitalio

SWITCH_MODE = digitalio.Pull.UP # Can be set to digitalio.Pull.DOWN
PRODUCTION_MODE_PIN = board.GP6  # Edit mode toggle switch pin

production_mode_switch = digitalio.DigitalInOut(PRODUCTION_MODE_PIN)
production_mode_switch.direction = digitalio.Direction.INPUT
production_mode_switch.pull = SWITCH_MODE


