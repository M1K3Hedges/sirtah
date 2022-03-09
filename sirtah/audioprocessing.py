from ulab import utils
from ulab import numpy as np

__all__ = [
	"get_volume",
	"audio2float"
]

UINT16MAX = (2**16)//2

def get_volume(samples):
	return np.sum(samples**2)/len(samples) * 100  

def audio2float(samples):
	samp32 = utils.from_uint16_buffer(samples) - UINT16MAX
	samp32 /= UINT16MAX
	#samp32 = (samp32 - .5) * 2.
	return samp32


