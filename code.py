import time
import array
import board
import audiobusio
import analogio
import pwmio
import math
import pitch
from ulab import numpy as np
from sirtah.constants import audioparams, get_pitch_difference, get_coin_output_value
from sirtah.audioprocessing import remove_dc, normalized_rms, MovingAverage


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

    # Output to Coin Vibration Motor
    cvm = pwmio.PWMOut(board.GP17, frequency = 250, variable_frequency = True)

    #buffer, fs, threshold
    pt = pitch.Yin(
        audioparams["buffersize"],
        audioparams["sample_rate"],
        0.15
    )

    BUFLEN = 4
    #avgbuffer = [0 for _ in range(BUFLEN)]
    f0_mavg = MovingAverage(buflen=BUFLEN)
    cn_mavg = MovingAverage(buflen=BUFLEN)

    coin_out = 0

    while True: #for _ in range(25):

        mic.record(samples, audioparams["buffersize"])
        f0_pre = pt.getPitch(samples)

        # Only picks up input if pitch found
        if int(f0_pre) == -1:
           f0_mavg.update(0)
           cn_mavg.update(0)

           if int(cn_mavg.get()) == 0:
               cvm.duty_cycle = 1

           continue

        # -----> Process the pitch from here
        f0_raw = f0_pre / 2

        # Update moving avg buffer
        f0_mavg.update(f0_raw)

        # Compute moving avg
        f0_estimate = f0_mavg.get()

        #
        fdiff, idx, target = get_pitch_difference(f0_estimate)

        #
        coin_out_raw = get_coin_output_value(fdiff, idx)
        cn_mavg.update(coin_out_raw)

        coin_out = cn_mavg.get()
        cvm.duty_cycle = int(coin_out) if coin_out > 0 else 1

        # -----> Printing
        print("f0 est: ", f0_estimate)
        print(f"fdiff: {fdiff}, target: {target}")
        print(f"coin out: {coin_out}")

        # -----> END OF LOOP UPDATES
        time.sleep(0.01)

    print("program done")

if __name__ == "__main__":
    main()
