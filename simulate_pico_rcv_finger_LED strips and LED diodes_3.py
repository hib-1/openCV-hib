# 7/29  led strip and led diodes rcv finger data V3
#must close thonny
import sys
import select
import array
from machine import Pin
import rp2

# --- PIO Program for WS2812B ---
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT,
             autopull=True, pull_thresh=24)
def ws2812():
    T1, T2, T3 = 2, 5, 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()

# --- Configuration ---
NUM_STRIPS = 5
NUM_LEDS = 15
DATA_PINS = [5, 6, 7, 8, 9]
SINGLE_LED_PINS = [14, 15, 13]
BRIGHTNESS = 0.4

# --- Initialize Diodes ---
diodes = [Pin(pin, Pin.OUT) for pin in SINGLE_LED_PINS]

# --- Initialize State Machines and Buffers ---
sms = []
buffers = []

for i in range(NUM_STRIPS):
    sm = rp2.StateMachine(i, ws2812, freq=8_000_000, sideset_base=Pin(DATA_PINS[i]))
    sm.active(1)
    sms.append(sm)
    buffers.append(array.array("I", [0 for _ in range(NUM_LEDS)]))

# --- RGB to GRB Converter ---
def rgb_to_grb(r, g, b):
    r = int(r * BRIGHTNESS)
    g = int(g * BRIGHTNESS)
    b = int(b * BRIGHTNESS)
    return (g << 16) | (r << 8) | b

# --- Update One Strip’s Buffer ---
def pixels_fill(strip, color):
    if 0 <= strip < NUM_STRIPS:
        grb = rgb_to_grb(*color)
        for i in range(NUM_LEDS):
            buffers[strip][i] = grb

# --- Push Buffers to All State Machines ---
def pixels_show():
    for i in range(NUM_STRIPS):
        sms[i].put(buffers[i], 8)

# --- Light Selected Strips, Turn Off Others ---
def delight_strips(strips, color):
    for i in range(NUM_STRIPS):
        if i in strips:
            pixels_fill(i, color)
        else:
            pixels_fill(i, (0, 0, 0))
    pixels_show()

# --- Main Loop: Listen for Serial Finger Data ---
print("Waiting for serial input...")
while True:
    if select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()
        if len(line) == NUM_STRIPS and all(c in "01" for c in line):
            active_strips = []
            for idx, state in enumerate(line):
                # Set diode ON/OFF
                if idx < len(diodes):
                    diodes[idx].value(int(state))

                if state == "1":
                    active_strips.append(idx)

            delight_strips(active_strips, (255, 255, 255))  # White on active strips