# LED setup
led = Pin(16, Pin.OUT)

# Button setup
button1 = Pin(10, Pin.IN, Pin.PULL_UP)
button2 = Pin(11, Pin.IN, Pin.PULL_UP)

# Rotary encoder setup
enc1_A = Pin(12, Pin.IN, Pin.PULL_UP)
enc1_B = Pin(13, Pin.IN, Pin.PULL_UP)
enc2_A = Pin(14, Pin.IN, Pin.PULL_UP)
enc2_B = Pin(15, Pin.IN, Pin.PULL_UP)

# Variables for encoder states
enc1_last = enc1_A.value()
enc2_last = enc2_A.value()

# Button debounce delay
debounce_time = 50  

def check_buttons():
    global debounce_time
    if button1.value() == 0:  # Active LOW
        print("Button 1 Pressed")
        led.toggle()
        time.sleep_ms(debounce_time)

    if button2.value() == 0:  # Active LOW
        print("Button 2 Pressed")
        time.sleep_ms(debounce_time)

def check_encoder(enc_A, enc_B, last_state):
    state = enc_A.value()
    if state != last_state:
        if enc_B.value() != state:
            print("Rotary Encoder: Clockwise")
        else:
            print("Rotary Encoder: Counter-Clockwise")
    return state

while True:
    check_buttons()
    enc1_last = check_encoder(enc1_A, enc1_B, enc1_last)
    enc2_last = check_encoder(enc2_A, enc2_B, enc2_last)
    time.sleep_ms(10)  # Short delay for stability