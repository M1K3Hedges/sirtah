#ifndef MICROPY_INCLUDED_SHARED_BINDINGS_PITCH_YIN_H
#define MICROPY_INCLUDED_SHARED_BINDINGS_PITCH_YIN_H

#include "shared-module/pitch/Yin.h"

extern const mp_obj_type_t pitch_yin_type;

void shared_module_pitch_yin_construct(pitch_yin_obj_t* self, uint16_t bufferSize, uint16_t sampleRate, float threshold);

void shared_module_pitch_yin_deinit(pitch_yin_obj_t* self);

bool shared_module_pitch_yin_deinited(pitch_yin_obj_t* self);

float shared_module_pitch_yin_getPitch(pitch_yin_obj_t* self, uint16_t *buffer);

float shared_module_pitch_yin_getProbability(pitch_yin_obj_t* self);

/*
extern void 
shared_module_pitch_yin_construct(pitch_yin_obj_t* self, uint16_t bufferSize, uint16_t sampleRate, float threshold);

extern void
shared_module_pitch_yin_deinit(pitch_yin_obj_t* self);

extern bool
shared_module_pitch_yin_deinited(pitch_yin_obj_t* self);

extern float
shared_module_pitch_yin_getPitch(pitch_yin_obj_t* self, uint16_t *buffer);

extern float
shared_module_pitch_yin_getProbability(pitch_yin_obj_t* self);
*/

#endif //MICROPY_INCLUDED_SHARED_BINDINGS_PITCH_YIN_H