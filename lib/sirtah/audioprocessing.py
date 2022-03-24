from ulab import utils
from ulab import numpy as np
import math
import array

__all__ = [
	"get_volume",
    "remove_dc",
    "normalized_rms",
    "MovingAverage"
]

UINT16MAX = (2**16)//2

class MovingAverage():

    def __init__(self, buflen):
        self.buflen = buflen
        self.buffer = [
            0 for _ in range(self.buflen)
        ]

    def __rollbuf(self, value):
        for i in range(self.buflen - 1):
            self.buffer[i + 1] = self.buffer[i]
        self.buffer[0] = value


    def update(self, value):
        self.__rollbuf(value)

    def get(self):
        return sum(self.buffer) / self.buflen


def get_volume(samples):
	return np.sum(samples**2)/len(samples) * 100

# Return Microphone Levels
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values)

    return math.sqrt(samples_sum / len(values))

def remove_dc(values, inplace=True):
    return values - np.mean(values)

# Average Microphone Levels/Remove DC Bias
def mean(values):
    return sum(values) // len(values)
