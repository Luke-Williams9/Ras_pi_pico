"""
Environment Configuration for Raspberry Pi Pico Macro Pad

This module defines environment-specific settings and pins for the macro pad.
The key configuration is the edit mode switch pin, which determines whether
the device runs in development (edit) mode or production mode.

Edit Mode Switch:
    - Connected to GPIO22 (Physical Pin 29)
    - Pull-down enabled (switch should connect to 3.3V)
    - HIGH = Edit Mode (USB drive and console enabled)
    - LOW = Production Mode (USB drive and console disabled)

This configuration is used by both boot.py and code.py to determine the
operating mode of the device.
"""

import board, digitalio

EDIT_MODE_PIN = board.GP22  # Edit mode toggle switch pin
edit_mode_switch = digitalio.DigitalInOut(EDIT_MODE_PIN)
edit_mode_switch.direction = digitalio.Direction.INPUT
edit_mode_switch.pull = digitalio.Pull.DOWN
