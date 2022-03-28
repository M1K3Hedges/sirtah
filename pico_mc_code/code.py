import array
import audiobusio
import board
import math
import pitch
import pwmio
import time

from sirtah.audioprocessing import remove_dc, normalized_rms, MovingAverage
from sirtah.noteprocessing import audioparams, get_pitch_difference, get_cvm_output_value
from ulab import numpy as np

### OPERATION SECTION ###

def main():

    # Microphone Input
    mic = audiobusio.PDMIn(
        board.GP19,
        board.GP18,
        sample_rate = audioparams["sample_rate"],
        bit_depth = 16,
        mono = True
    )

    samples = array.array('H', [0] * audioparams["buffersize"])

    # Pitch Tracker, YIN Method
    pt = pitch.Yin(
        audioparams["buffersize"],  # Buffer
        audioparams["sample_rate"], # Sampling Rate
        0.15 #Threshold
    )

    BUFLEN = 4 #Buffer Length
    f0_mavg = MovingAverage(buflen=BUFLEN) # F0 Moving Average
    cvm_mavg = MovingAverage(buflen=BUFLEN) # Coin Vibration Motor Average

    # Output to Coin Vibration Motor
    cvm = pwmio.PWMOut(board.GP17, frequency = 250, variable_frequency = True)

    cvm_out = 0

    while True:

        # Microphone 'Record'
        mic.record(samples, audioparams["buffersize"])

        # Preliminary Pitch Estimation
        f0_pre = pt.getPitch(samples)

        # Only picks up input if pitch found
        if int(f0_pre) == -1:
           f0_mavg.update(0)
           cvm_mavg.update(0)

           if int(cvm_mavg.get()) == 0:
               cvm.duty_cycle = 1

           continue

        # Begin Processing of Pitch
        f0_raw = f0_pre / 2

        # Update Moving Average Buffer
        f0_mavg.update(f0_raw)

        # Compute Moving Average
        f0_estimate = f0_mavg.get()

        # Obtain Frequency Difference, Index and Target Frequency
        fdiff, idx, target = get_pitch_difference(f0_estimate)

        # Obtain Value for Vibration Motor Output
        cvm_out_raw = get_cvm_output_value(fdiff, idx)
        cvm_mavg.update(cvm_out_raw)

        cvm_out = cvm_mavg.get()
        cvm.duty_cycle = int(cvm_out) if cvm_out > 0 else 1

        # Printing
        #print("f0 est: ", f0_estimate)
        #print(f"fdiff: {fdiff}, target: {target}")
        #print(f"coin out: {cvm_out}")

        # End of Loop Updates
        time.sleep(0.01)

    #print("program done")

if __name__ == "__main__":
    main()
