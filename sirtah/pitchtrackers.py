#import aubio.pitch
from ulab import numpy as np

# Custom imports
from .constants import audioparams
from .audioprocessing import get_volume

__all__ = [
	"PitchValues"
]

class PitchValues(object):
	def __init__(self):
		pass
		# Initializes aubio YIN pitch estimation
		#self.YINdetector = aubio.pitch(
		#	"default", audioparams["buffersize"], audioparams["buffersize"], audioparams["sample_rate"])
		#self.YINdetector.set_unit("Hz")
		#self.YINdetector.set_silence(-40)
	
	def handleYIN(self, samples):
		pass
		#volume = get_volume(samples)
		#pitch_out  = self.YINdetector(samples)[0]

		#if not pitch_out or volume < audioparams["volume_thresh"]:
		#	return None

		#return pitch_out

	# Accesses CREPE data
	#def handleCREPE(self, samples):
	#	return crepe.predict(samples, audioparams["FS"], viterbi = True)[1][0]

	# Extracts and evaluates audio signal and queues it
	'''
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