#include <stdint.h> /* For extended integer types */

#include "py/runtime.h"

#include "Yin.h"
#include "supervisor/shared/translate.h"

/* Default values if none is supplied */
#define YIN_DEFAULT_SAMPLING_RATE 44100
#define YIN_DEFAULT_THRESHOLD     0.15

/* Some helper macros for uint-to-int type casting */
#define AUDIO_INT16_MAX (INT16_MAX + 1)
#define AUDIO_UINT16_TO_INT16_T(t) ((int16_t) (t)) + AUDIO_INT16_MAX

/**
 * PRIVATE METHOD
 * Step 1: Calculates the squared difference of the signal with a shifted version of itself.
 * @param buffer Buffer of samples to process. 
 *
 * This is the Yin algorithms tweak on autocorellation. Read http://audition.ens.fr/adc/pdf/2002_JASA_YIN.pdf
 * for more details on what is in here and why it's done this way.
 */
void Yin_difference(pitch_yin_obj_t* self, uint16_t* buffer){
	int16_t i, tau, t0, t1;
	float delta;

	/* Calculate the difference for difference shift values (tau) for the half of the samples */
	for(tau = 0 ; tau < self->halfBufferSize; tau++){

		/* Take the difference of the signal with a shifted version of itself, then square it.
		 * (This is the Yin algorithm's tweak on autocorellation) */ 
		for(i = 0; i < self->halfBufferSize; i++){
			
			/* Perform typecasting "in-place" since this is
			 * the only place in the algo where we need these values. */
			t0 = AUDIO_UINT16_TO_INT16_T(buffer[i]);
			t1 = AUDIO_UINT16_TO_INT16_T(buffer[i + tau]);
			
			delta = t0 - t1;
			self->yinBuffer[tau] += delta * delta;
		}
	}
}

/**
 * PRIVATE METHOD
 * Step 2: Calculate the cumulative mean on the normalised difference calculated in step 1
 * @param yin #Yin structure with information about the signal
 *
 * This goes through the Yin autocorellation values and finds out roughly where shift is which 
 * produced the smallest difference
 */
void Yin_cumulativeMeanNormalizedDifference(pitch_yin_obj_t* self){
	uint16_t tau;
	float runningSum = 0;
	self->yinBuffer[0] = 1;

	/* Sum all the values in the autocorellation buffer and nomalise the result, replacing
	 * the value in the autocorellation buffer with a cumulative mean of the normalised difference */
	for (tau = 1; tau < self->halfBufferSize; tau++) {
		runningSum += self->yinBuffer[tau];
		self->yinBuffer[tau] *= tau / runningSum;
	}
}

/**
 * PRIVATE METHOD
 * Step 3: Search through the normalised cumulative mean array and find values that are over the threshold
 * @return Shift (tau) which caused the best approximate autocorellation. -1 if no suitable value is found over the threshold.
 */
int16_t Yin_absoluteThreshold(pitch_yin_obj_t* self){
	int16_t tau;

	/* Search through the array of cumulative mean values, and look for ones that are over the threshold 
	 * The first two positions in yinBuffer are always so start at the third (index 2) */
	for (tau = 2; tau < self->halfBufferSize ; tau++) {
		if (self->yinBuffer[tau] < self->threshold) {
			while (tau + 1 < self->halfBufferSize && self->yinBuffer[tau + 1] < self->yinBuffer[tau]) {
				tau++;
			}
			/* found tau, exit loop and return
			 * store the probability
			 * From the YIN paper: The yin->threshold determines the list of
			 * candidates admitted to the set, and can be interpreted as the
			 * proportion of aperiodic power tolerated
			 * within a periodic signal.
			 *
			 * Since we want the periodicity and and not aperiodicity:
			 * periodicity = 1 - aperiodicity */
			self->probability = 1 - self->yinBuffer[tau];
			break;
		}
	}

	/* if no pitch found, tau => -1 */
	if (tau == self->halfBufferSize || self->yinBuffer[tau] >= self->threshold) {
		tau = -1;
		self->probability = 0;
	}

	return tau;
}

/**
 * Step 5: Interpolate the shift value (tau) to improve the pitch estimate.
 * @param  yin         [description]
 * @param  tauEstimate [description]
 * @return             [description]
 *
 * The 'best' shift value for autocorellation is most likely not an interger shift of the signal.
 * As we only autocorellated using integer shifts we should check that there isn't a better fractional 
 * shift value.
 */
float Yin_parabolicInterpolation(pitch_yin_obj_t* self, int16_t tauEstimate) {
	float betterTau;
	int16_t x0, x2;
	
	/* Calculate the first polynomial coeffcient based on the current estimate of tau */
	if (tauEstimate < 1) {
		x0 = tauEstimate;
	} 
	else {
		x0 = tauEstimate - 1;
	}

	/* Calculate the second polynomial coeffcient based on the current estimate of tau */
	if (tauEstimate + 1 < self->halfBufferSize) {
		x2 = tauEstimate + 1;
	} 
	else {
		x2 = tauEstimate;
	}

	/* Algorithm to parabolically interpolate the shift value tau to find a better estimate */
	if (x0 == tauEstimate) {
		if (self->yinBuffer[tauEstimate] <= self->yinBuffer[x2]) {
			betterTau = tauEstimate;
		} 
		else {
			betterTau = x2;
		}
	} 
	else if (x2 == tauEstimate) {
		if (self->yinBuffer[tauEstimate] <= self->yinBuffer[x0]) {
			betterTau = tauEstimate;
		} 
		else {
			betterTau = x0;
		}
	} 
	else {
		float s0, s1, s2;
		s0 = self->yinBuffer[x0];
		s1 = self->yinBuffer[tauEstimate];
		s2 = self->yinBuffer[x2];
		// fixed AUBIO implementation, thanks to Karl Helgason:
		// (2.0f * s1 - s2 - s0) was incorrectly multiplied with -1
		betterTau = tauEstimate + (s2 - s0) / (2 * (2 * s1 - s2 - s0));
	}

	return betterTau;
}


void shared_module_pitch_yin_construct(pitch_yin_obj_t* self, uint16_t bufferSize, uint16_t sampleRate, float threshold){
	/* Initialise the fields of the Yin structure passed in */
	self->bufferSize = bufferSize;
	self->halfBufferSize = bufferSize / 2;
	self->sampleRate = sampleRate;
	self->probability = 0.0;
	self->threshold = threshold;

	/* Allocate the autocorellation buffer and initialise it to zero */
	self->yinBuffer = (float *) m_malloc(sizeof(float) * self->halfBufferSize, false);
	if (!self->yinBuffer){
		self->yinBuffer = NULL;
		return;
	}

	uint16_t i;
	for (i = 0; i < self->halfBufferSize; i++){
		self->yinBuffer[i] = 0;
	}
}

bool shared_module_pitch_yin_deinited(pitch_yin_obj_t* self){
	return self->yinBuffer == NULL;
}

void shared_module_pitch_yin_deinit(pitch_yin_obj_t* self){
	/* Check if resources have already been released */
	if (shared_module_pitch_yin_deinited(self)){
		return;
	}
	/* Release all resources used by this instance */
	m_free(self->yinBuffer);
	self->yinBuffer = NULL;
}

float shared_module_pitch_yin_getPitch(pitch_yin_obj_t* self, uint16_t *buffer){
	int16_t tauEstimate = -1;
	float pitchInHertz = -1;
	
	/* Step 1: Calculates the squared difference of the signal with a shifted version of itself. */
	Yin_difference(self, buffer);
	
	/* Step 2: Calculate the cumulative mean on the normalised difference calculated in step 1 */
	Yin_cumulativeMeanNormalizedDifference(self);
	
	/* Step 3: Search through the normalised cumulative mean array and find values that are over the threshold */
	tauEstimate = Yin_absoluteThreshold(self);
	
	/* Step 5: Interpolate the shift value (tau) to improve the pitch estimate. */
	if (tauEstimate != -1){
		pitchInHertz = self->sampleRate / Yin_parabolicInterpolation(self, tauEstimate);
	}
	return pitchInHertz;
}

float shared_module_pitch_yin_getProbability(pitch_yin_obj_t* self){
	return self->probability;
}








