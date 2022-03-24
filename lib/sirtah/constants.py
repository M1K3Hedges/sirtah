from ulab import numpy as np

__all__ = [
	"freqs",
	"audioparams",
	"get_pitch_difference",
    "get_coin_output_value"
]

# Audio parameters
audioparams = {
	"sample_rate": 44100,
	"channels": 1,
	"buffersize": 512,
	"volume_thresh": 0.01
}

target_freqs = np.array([
	77.78, 82.41, 87.31, 92.5, 98, 103.83,
    110, 116.54, 123.47, 130.81, 138.59, 146.83,
    155.56, 164.81, 174.61, 185, 196, 207.65,
    220, 233.08, 246.94, 261.63, 277.18, 293.66,
    311.13, 329.63, 349.23, 369.99, 392, 415.3,
    440, 466.16, 493.88, 523.25, 554.37, 587.33,
    622.25, 659.26, 698.46, 739.99, 783.99, 830.61,
    880, 932.33, 987.77, 1046.5, 1108.73, 1174.66,
    1244.51, 1318.51, 1396.91
])

freq_interval_tresholds = [
    (2.315, 2.45), (2.45, 2.595), (2.595, 2.75),
    (2.75, 2.915), (2.915, 3.085), (3.085, 3.27),
    (3.27, 3.465), (3.465, 3.67), (3.67, 3.89),
    (3.89, 4.12), (4.12, 4.365), (4.365, 4.625),
    (4.625, 4.9), (4.9, 5.195), (5.195, 5.5),
    (5.5, 5.825), (5.825, 6.175), (6.175, 6.54),
    (6.54, 6.93), (6.93, 7.345), (7.345, 7.775),
    (7.775, 8.24), (8.24, 8.735), (8.735, 9.25),
    (9.25, 9.8), (9.8, 10.38), (10.38, 11.005),
    (11.005, 11.65), (11.65, 12.35), (12.35, 13.08),
    (13.08, 13.86), (13.86, 14.685), (14.685, 15.56),
    (15.56, 16.48), (16.48, 17.46), (17.46, 18.505),
    (18.505, 19.6), (19.6, 20.765), (20.765, 22.0),
    (22.0, 23.31), (23.31, 24.695), (24.695, 26.165),
    (26.165, 27.72), (27.72, 29.365), (29.365, 31.115),
    (31.115, 32.965), (32.965, 34.925), (34.925, 37.0),
    (37.0, 38.84)
]

MIN_COIN_OUT = 0
MAX_COIN_OUT = 65535
HALF_COIN_OUT = 32768

def make_interp(lmin, lmax, rmin, rmax):
    ls = lmax - lmin
    rs = rmax - rmin
    scf = rs / ls
    def interp_fn(x):
        return rmin + (x-lmin)*scf
    return interp_fn

SCALERS = [
    make_interp(
        -freq_interval_tresholds[i][0],
        freq_interval_tresholds[i][1],
        MIN_COIN_OUT, MAX_COIN_OUT
    ) for i in range(len(freq_interval_tresholds))
]

FINAL_SCALER = make_interp(
    -32768, 32767, MIN_COIN_OUT, MAX_COIN_OUT
)

def quick_abs(arr):
    return np.array([
        abs(arr[i]) for i in range(len(arr))
    ])

# Generating note and frequency value relationship
def get_pitch_difference(pitch):
    fdiff = quick_abs(target_freqs - pitch) #np.abs(target_freqs - pitch)
    idx = np.argmin(fdiff)
    desired_freq = target_freqs[idx]
    diff_to_return = pitch - desired_freq #(freqs - pitch)[idx]
    return diff_to_return, idx, desired_freq

def get_coin_output_value(freq_diff, idx):
    scaler = SCALERS[idx]
    scale_diff = scaler(freq_diff) - HALF_COIN_OUT
    return FINAL_SCALER(scale_diff)

