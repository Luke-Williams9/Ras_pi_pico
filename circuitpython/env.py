import board, digitalio

SWITCH_MODE = digitalio.Pull.UP # Can be set to digitalio.Pull.DOWN
PRODUCTION_MODE_PIN = board.GP24  # Edit mode toggle switch pin

# set to True to disable keyboard / mouse output
TEST_MODE=False 
# TEST_MODE=True
production_mode_switch = digitalio.DigitalInOut(PRODUCTION_MODE_PIN)
production_mode_switch.direction = digitalio.Direction.INPUT
production_mode_switch.pull = SWITCH_MODE


