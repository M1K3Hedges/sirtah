# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import array
import math
import board
import audiobusio
import pwmio
import analogio

mic_in = analogio.AnalogIn(board.GP28)

# Average Microphone Levels/Remove DC Bias
def mean(values):
    return sum(values) / len(values)

# Return Microphone Levels
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )

    return math.sqrt(samples_sum / len(values))


# Main program
mic = audiobusio.PDMIn(board.GP3, board.GP2, sample_rate = 16000, bit_depth = 16, mono = True)
samples = array.array('H', [0] * 160)

#Coin Vibration Motor
cvm = pwmio.PWMOut(board.GP6, frequency = 500, variable_frequency=True)

while True:
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    print((samples,))
    cvm.duty_cycle = 0
    time.sleep(0.1)
