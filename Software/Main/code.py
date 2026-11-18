# FileCopyrightText: 2026 Stephen Goadhouse, UVa Physics Electronics Shop
#
# Based heavily on the pioasm example, pioasm_background_morse.py,
# included in the Adafruit CircuitPython library bundle.
# Original Copyright for this file:
# SPDX-FileCopyrightText: 2022 Jeff Epler, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Use a PIO to output a pulse sequence in order to use to synchronize with

The combination of "OUT status" and duration is sent to the PIO as
16-bit number: The top bit is 1 if the OUT is driven high and 0 for
driven low.  The other 15 bits form a delay value from 1 to 32767. A
single time unit is configured to be 100 ms (10kHz / 25 / 40). The
largest delay is 32767 / (40 * 10) = 81.9175 seconds.

"""

import array
import time
import board
import neopixel

from rp2pio import StateMachine

from adafruit_pioasm import Program

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.3
# Set to RED while initializing
pixel.fill((255, 0, 0))

# This program turns the OUT high or low depending on the first bit of the value,
# then delays a length of time given by the next 15 bits of the value.
pio_code = Program(
    """
        out x, 1
        mov pins, x
        out x, 15
    busy_wait:
        jmp x--, busy_wait [24]
        """
)


# The top bit of the command is the OUT value, high or low
OUT_HI = 0x8000
OUT_LO = 0x0000

# The other 15 bits are a delay duration.
# Max 8191 100ms units
HUNDO_MS = 40

# 
# Pattern will starts with 11 100 ms pulses that are spaced 5s apart
PULSE_5S = array.array("H", [OUT_HI | HUNDO_MS, OUT_LO | (49 * HUNDO_MS)])
# Followed by a single triple-burst marker
TRIPLE_BURST = array.array("H", [OUT_HI | HUNDO_MS, OUT_LO | (2 * HUNDO_MS)]) * 3
# Fill so the cycle is exactly 60s
MIN_FILL = array.array("H", [OUT_LO, (600 - ((1 + 49)*11) - ((1 + 2)*3)) * HUNDO_MS])

# Combine them all into the Sequence
SEQ = (PULSE_5S * 11) + TRIPLE_BURST + MIN_FILL

## Create similar timed pattern for RED LED but give the ON time longer than 100 ms so it can be seen
LED_PULSE_5S = array.array("H", [OUT_HI | (7 * HUNDO_MS), OUT_LO | (43 * HUNDO_MS)])
LED_SEQ = (LED_PULSE_5S * 11) + TRIPLE_BURST + MIN_FILL

sm = StateMachine(
    pio_code.assembled,
    frequency=10_000,
    first_out_pin=board.D12,
    pull_threshold=16,
    auto_pull=True,
    out_shift_right=False,
    **pio_code.pio_kwargs,
)

# Setup a similar state machine for the LED, but with the 5S pulse
# holding a little longer so that the LED is more easily visable. This
# gives indication of what is happening with the sync sequence
# although not at the exact same moment since a different state
# machine than the one driving D12. This has to be a different state
# machine as the LED and D12 are not adjacent I/O.
smLed = StateMachine(
    pio_code.assembled,
    frequency=10_000,
    first_out_pin=board.LED,
    pull_threshold=16,
    auto_pull=True,
    out_shift_right=False,
    **pio_code.pio_kwargs,
)

## Output frequencies to make sure they are as expected. 150 MHz for RP2350 and 10kHz for both PIO state machines.
import microcontroller
sys_freq = microcontroller.cpu.frequency  # e.g., 125000000 for RP2040
print("CPU Frequency:", sys_freq)
print("SM Frequency:", sm.frequency)
print("SM LED Frequency:", smLed.frequency)

print("Sending out Sync sequence forever", end="")
sm.background_write(loop=SEQ)
smLed.background_write(loop=LED_SEQ)

# Set to Green while running
pulse = [0.8, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.075, 0.05, 0.037, 0.025, 0.012, 0.025, 0.037, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6]
idx = 0
pixel.brightness = pulse[0]
pixel.fill((0, 255, 0))
while True:
    if idx == 0: print(end=".") 
    idx = (idx + 1) % len(pulse)
    pixel.brightness = pulse[idx]
    time.sleep(0.2)

