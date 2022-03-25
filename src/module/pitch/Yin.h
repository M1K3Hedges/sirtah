#ifndef MICROPY_INCLUDED_PITCH_YIN_H
#define MICROPY_INCLUDED_PITCH_YIN_H

#include "py/obj.h"
#include <stdint.h>

typedef struct {
	mp_obj_base_t base;
	uint16_t bufferSize;
	uint16_t halfBufferSize;
	uint16_t sampleRate;
	float* yinBuffer;
	float probability;
	float threshold;
} pitch_yin_obj_t;

void Yin_difference(pitch_yin_obj_t* self, uint16_t* buffer);
void Yin_cumulativeMeanNormalizedDifference(pitch_yin_obj_t* self);
int16_t Yin_absoluteThreshold(pitch_yin_obj_t* self);
float Yin_parabolicInterpolation(pitch_yin_obj_t* self, int16_t tauEstimate);

void shared_module_pitch_yin_construct(pitch_yin_obj_t* self, uint16_t bufferSize, uint16_t sampleRate, float threshold);
bool shared_module_pitch_yin_deinited(pitch_yin_obj_t* self);
void shared_module_pitch_yin_deinit(pitch_yin_obj_t* self);
float shared_module_pitch_yin_getPitch(pitch_yin_obj_t* self, uint16_t *buffer);
float shared_module_pitch_yin_getProbability(pitch_yin_obj_t* self);

#endif // MICROPY_INCLUDED_PITCH_YIN_H