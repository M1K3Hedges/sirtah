import array
import audiobusio
import board
import math
import pwmio
import time
from ulab import utils
from ulab import numpy as np
from sirtah.constants import audioparams
from sirtah.audioprocessing import audio2float
from sirtah.yin import compute_yin

#from sirtah.pitchtrackers import PitchValues

### AUDIO SECTION ###
# Audio Parameters
#fs = 44100
#buffersize = 2048
#volume_thresh = 0.01

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

### HAPTIC SECTION ###
'''
def duty_cycle_update(cvm):
    freq_percent = des_freq * 0.01

    if abs(freqDiff) > freq_percent:
        cvm.duty_cycle = int(65535/freqDiff)
    else:
        cvm.duty_cycle = 0
'''

### OPERATION SECTION ###

def main():

    # Microphone Input
    mic = audiobusio.PDMIn(
        board.GP3,
        board.GP2,
        sample_rate = audioparams["sample_rate"],
        bit_depth = 16,
        mono = True
    )

    samples = array.array('H', [0] * audioparams["buffersize"])
    #np.empty((audioparams["buffersize"], ), dtype=np.uint16)

    # Output to Coin Vibration Motor
    cvm = pwmio.PWMOut(board.GP6, frequency = 500, variable_frequency = True)

    for _ in range(100):
        try:

            mic.record(samples, audioparams["buffersize"])
            samps32 = utils.from_uint16_buffer(samples) #audio2float(samples)
            #samps32 -= (2**16)//2
            #samps32 /= (2**16)//2

            #print(normalized_rms(samples))
            #print(min(samps32), max(samps32))

            f0s, hrs, amins, ts = compute_yin(
                sig = samps32,
                sr  = audioparams["sample_rate"],
                w_len = audioparams["buffersize"],
                w_step = audioparams["buffersize"] // 2,
                f0_min = 20,
                f0_max = 22000,
                harmo_thresh = 0.1
            )

            print(f0s, hrs, amins, ts)
            time.sleep(0.01)
        except Exception as e:
            print(e)
            break

    print("program done")

if __name__ == "__main__":
    main()

'''
while True:
    try:
        testfunc()
    except KeyboardInterrupt as e:
        print("quitting infinite loop")
        break
    time.sleep(0.1)

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
'''
