'''
import aubio
import crepe
import queue
import time
from ulab import numpy as np

# Audio parameters
audioparams = {
	"FS": 44100,
	"channels": 1,
	"buffersize": 2048,
	"volume_thresh": 0.01}

class PitchValues(object):
	def __init__(self):

		# Initializes aubio YIN pitch estimation
		self.YINdetector = aubio.pitch(
			"default", audioparams["buffersize"], audioparams["buffersize"], audioparams["FS"])
		self.YINdetector.set_unit("Hz")
		self.YINdetector.set_silence(-40)
	
	def handleYIN(self, samples):
		return self.YINdetector(samples)[0]

	# Accesses CREPE data
	def handleCREPE(self, samples):
		return crepe.predict(samples, audioparams["FS"], viterbi = True)[1][0]

	# Extracts and evaluates audio signal and queues it
	def audioloop(self):

		while True:
			data = self.stream.read(
				audioparams["buffersize"]//2, exception_on_overflow = False)
			samples = np.fromstring(data, dtype=np.float32)

			pitchYIN = self.handleYIN(samples)
			pitchCREPE = self.handleCREPE(samples)

			# Computes the energy (volume) of the current frame
			volume = np.sum(samples**2)/len(samples) * 100

			if not pitchYIN or volume < audioparams["volume_thresh"]:
				continue

			if not pitchCREPE or volume < audioparams["volume_thresh"]:
				continue

			self.q.put({"yin": pitchYIN, "crepe": pitchCREPE})

	def close(self):
		self.stream.stop_stream()
		self.stream.close()
'''
