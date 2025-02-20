import storage, supervisor, usb_cdc
from env import production_mode_switch

# By default (with no GP pins connected), we should be in edit mode
# Check if we're in production mode (switch ON = pull-up to HIGH)
production_mode = production_mode_switch.value

if production_mode:
    # Production mode: Disable USB drive and console, ensure code.py runs
    storage.disable_usb_drive()
    usb_cdc.enable(console=False, data=False)  # Disable REPL to ensure clean auto-run
    supervisor.runtime.auto_reload = False  # Disable auto-reload in production
else:
    # Edit mode ON: Enable USB drive and console
    storage.enable_usb_drive()
    usb_cdc.enable(console=True, data=False)
    supervisor.runtime.auto_reload = True
    


