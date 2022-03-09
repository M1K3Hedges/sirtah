import array
import aubio
import audiobusio
import board
import crepe
import math
import pitchtrack as pt
import pwmio
import threading as Thread
import time
from ulab import numpy as np

pe = pt.PitchValues()

### AUDIO SECTION ###

# Audio Parameters
fs = 44100
buffersize = 2048
volume_thresh = 0.01

# Average Microphone Levels/Remove DC Bias
def mean(values):
    return sum(values) / len(values)

# Return Microphone Levels
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values)

    return math.sqrt(samples_sum / len(values))

# Microphone Input
mic = audiobusio.PDMIn(board.GP3, board.GP2, sample_rate = fs, bit_depth = 16, mono = True)
samples = array.array('H', [0] * 160)

# Pre-defined Note Values (E2 to E6)
freqs = np.array([
	82.41, 87.31, 92.5, 98, 103.83,
    110, 116.54, 123.47, 130.81, 138.59, 146.83,
    155.56, 164.81, 174.61, 185, 196, 207.65,
    220, 233.08, 246.94, 261.63, 277.18, 293.66,
    311.13, 329.63, 349.23, 369.99, 392, 415.3,
    440,466.16, 493.88, 523.25, 554.37, 587.33,
    622.25, 659.26, 698.46,739.99, 783.99, 830.61,
    880, 932.33, 987.77, 1046.5, 1108.73, 1174.66,
    1244.51, 1318.51])

# Generating note and frequency value relationship
def get_note_info(pitch):
	fdiff = np.abs(freqs - pitch)
	idx   = np.argmin(fdiff)
	diff_to_return = (freqs - pitch)[idx]
	desired_freq = freqs[idx]

	return diff_to_return, desired_freq

def pitch_values(samples):
    YINdetector = aubio.pitch("default", buffersize, buffersize, fs)
    YINdetector.set_unit("Hz")
    YINdetector.set_silence(-40)

def handleYIN(samples):
    return YINdetector(samples)[0]

def handleCREPE(samples):
    return crepe.predict(samples, fs, viterbi = True)[1][0]



### HAPTIC SECTION ###

# Output to Coin Vibration Motor
cvm = pwmio.PWMOut(board.GP6, frequency = 500, variable_frequency = True)

def duty_cycle_update():
    freq_percent = des_freq * 0.01

    if abs(freqDiff) > freq_percent:
        cvm.duty_cycle = int(65535/freqDiff)
    else:
        cvm.duty_cycle = 0

### OPERATION SECTION ###

while True:
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    input_val = int(magnitude)

    pitchYIN = handleYIN(samples)
    pitchCREPE = handleCREPE(samples)

    # Computes the energy (volume) of the current frame
    volume = np.sum(samples**2)/len(samples) * 100

    if not pitchYIN or volume < volume_thresh:
        continue

    if not pitchCREPE or volume < volume_thresh:
        continue

    print((volume,))
    f0_val = handleYIN(samples)
    #f0_val = handleCREPE(samples)
    freqDiff, des_freq = nv.get_note_info(f0_val)

    duty_cycle_update()

    time.sleep(0.1)
