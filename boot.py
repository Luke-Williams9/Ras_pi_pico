"""
Boot Configuration Script for Raspberry Pi Pico Macro Pad

This script configures the Pico's USB and storage behavior based on the edit mode
switch state. It provides two operating modes:

1. Edit Mode (switch ON):
   - USB drive is enabled for file access
   - Serial console is enabled for debugging
   - Auto-reload is enabled for development

2. Production Mode (switch OFF):
   - USB drive is disabled for security
   - Serial console is disabled for clean operation
   - Auto-reload is disabled for stability

The edit mode state is determined by the EDIT_MODE_PIN defined in env.py
"""

import storage, supervisor, usb_cdc
from env import edit_mode_switch

# Check if we're in edit mode (switch ON = pull-up to HIGH)
edit_mode = edit_mode_switch.value

if edit_mode:
    # Edit mode ON: Enable USB drive and console for development
    print("Edit mode enabled")
    storage.enable_usb_drive()
    usb_cdc.enable(console=True, data=False)
    supervisor.runtime.auto_reload = True
else:
    # Production mode: Disable USB drive and console for clean operation
    storage.disable_usb_drive()
    usb_cdc.enable(console=False, data=False)  # Disable REPL to ensure clean auto-run
    supervisor.runtime.auto_reload = False  # Disable auto-reload in production