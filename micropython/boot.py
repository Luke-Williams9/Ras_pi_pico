import os
import storage
import usb_cdc

# Enable USB Mass Storage mode
storage.remount("/", readonly=False)
usb_cdc.enable(console=True, data=True)  # Keep REPL enabled