from ulab import numpy as np

__all__ = [
	"testfunc",
	"freqs",
	"audioparams",
	"get_note_info"
]

def testfunc():
	print(f"testing from {__name__}")


# Audio parameters
audioparams = {
	"sample_rate": 16000,
	"channels": 1,
	"buffersize": 2048,
	"volume_thresh": 0.01
}

freqs = np.array([
	82.41, 87.31, 92.5, 98, 103.83,
    110, 116.54, 123.47, 130.81, 138.59, 146.83,
    155.56, 164.81, 174.61, 185, 196, 207.65,
    220, 233.08, 246.94, 261.63, 277.18, 293.66,
    311.13, 329.63, 349.23, 369.99, 392, 415.3,
    440,466.16, 493.88, 523.25, 554.37, 587.33,
    622.25, 659.26, 698.46,739.99, 783.99, 830.61,
    880, 932.33, 987.77, 1046.5, 1108.73, 1174.66,
    1244.51, 1318.51
])

# Generating note and frequency value relationship
def get_note_info(pitch):
	fdiff = np.abs(freqs - pitch)
	idx   = np.argmin(fdiff)
	diff_to_return = (freqs - pitch)[idx]
	desired_freq = freqs[idx]

	return diff_to_return, desired_freq