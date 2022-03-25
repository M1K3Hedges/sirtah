#include <stdint.h>

#include "shared/runtime/context_manager_helpers.h"
#include "py/objproperty.h"
#include "py/runtime.h"
#include "py/runtime0.h"
#include "shared-bindings/pitch/Yin.h"
#include "shared-bindings/util.h"

//| .. currentmodule:: pitch
//|
//| :class:`Yin` -- perform f0 (fundamental frequency) estimation
//| 
STATIC mp_obj_t pitch_yin_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args){
	/* Declare an enum defining names of the input arguments */
	enum { ARG_bufferSize, ARG_sampleRate, ARG_threshold };

	static const mp_arg_t allowed_args[] = {
		{ 
			MP_QSTR_bufferSize, 
			MP_ARG_REQUIRED | MP_ARG_INT 
		},
		{ 
			MP_QSTR_sampleRate, 
			MP_ARG_REQUIRED | MP_ARG_INT 
		},
		{
			MP_QSTR_threshold,
			MP_ARG_REQUIRED | MP_ARG_OBJ 
		},
	};

	mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
	mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

	uint16_t bufferSize = args[ARG_bufferSize].u_int;
	uint16_t sampleRate = args[ARG_sampleRate].u_int;

	float threshold = 0.15;
	if (args[ARG_threshold].u_obj != mp_const_none){
		threshold = mp_obj_get_float(args[ARG_threshold].u_obj);
		if (threshold <= 0){
			threshold = 0.15;
		}
	}

	pitch_yin_obj_t *self = m_new_obj(pitch_yin_obj_t);
	self->base.type = &pitch_yin_type;

	shared_module_pitch_yin_construct(self, bufferSize, sampleRate, threshold); 

	return MP_OBJ_FROM_PTR(self);
}

//|   .. method:: deinit()
//|
//|      Deinitializes and releases any hardware resources for reuse.
//|
STATIC mp_obj_t pitch_yin_deinit(mp_obj_t self_in) {
	pitch_yin_obj_t *self = MP_OBJ_TO_PTR(self_in);
	shared_module_pitch_yin_deinit(self);
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(pitch_yin_deinit_obj, pitch_yin_deinit);

STATIC void check_for_deinit(pitch_yin_obj_t *self) {
	if (shared_module_pitch_yin_deinited(self)) {
		raise_deinited_error();
	}
}

//|   .. method:: __exit__()
//|
//|      Automatically deinitializes the hardware when exiting a context. See
//|      :ref:`lifetime-and-contextmanagers` for more info.
//|
STATIC mp_obj_t pitch_yin_obj___exit__(size_t n_args, const mp_obj_t *args) {
	(void)n_args;
	shared_module_pitch_yin_deinit(args[0]);
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(pitch_yin___exit___obj, 4, 4, pitch_yin_obj___exit__);


//|     def getPitch(self, buffer: ReadableBuffer) -> float:
//|         """ Performs pitch estimation on audiosamples stored in buffer """
//|         ...
//|
STATIC mp_obj_t pitch_yin_obj_getPitch(mp_obj_t self_obj, mp_obj_t buffer){
	/* Retrieve a C-pointer to our object */
	pitch_yin_obj_t *self = MP_OBJ_TO_PTR(self_obj);
	check_for_deinit(self);

	/* Fetch the underlying buffer storing our data */
	mp_buffer_info_t bufinfo;
	if (mp_get_buffer(buffer, &bufinfo, MP_BUFFER_READ)){
		float pitchEstimate = shared_module_pitch_yin_getPitch(self, bufinfo.buf);
		return mp_obj_new_float(pitchEstimate);
	}

	return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(pitch_yin_getPitch_obj, pitch_yin_obj_getPitch);


//|     def getProbability(self) -> float:
//|         """ Returns the probability of the f0 estimate being correct """
//|         ...
//|
STATIC mp_obj_t pitch_yin_obj_getProbability(mp_obj_t self_obj){
	/* Retrieve a C-pointer to our object */
	pitch_yin_obj_t *self = MP_OBJ_TO_PTR(self_obj);
	check_for_deinit(self);
	return mp_obj_new_float(shared_module_pitch_yin_getProbability(self));
}
MP_DEFINE_CONST_FUN_OBJ_1(pitch_yin_getProbability_obj, pitch_yin_obj_getProbability);


/* 
*
*
* PERFORM REMAINING SETUP
*
*/

/* DEFINE PROPERTIES OF OBJECT */
const mp_obj_property_t pitch_yin_prob_obj = {
	.base.type = &mp_type_property,
	.proxy = {
		(mp_obj_t)&pitch_yin_getProbability_obj,
		MP_ROM_NONE,
		MP_ROM_NONE
	}
};

/* DEFINE METHODS OF OBJECT 
 * (and link property from above) */
STATIC const mp_rom_map_elem_t pitch_yin_locals_dict_table[] = {
	// Methods
	{ MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&pitch_yin_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR___enter__), MP_ROM_PTR(&default___enter___obj) },
	{ MP_ROM_QSTR(MP_QSTR___exit__), MP_ROM_PTR(&pitch_yin___exit___obj) },
	{ MP_ROM_QSTR(MP_QSTR_getPitch), MP_ROM_PTR(&pitch_yin_getPitch_obj) },
	{ MP_ROM_QSTR(MP_QSTR_probability), MP_ROM_PTR(&pitch_yin_prob_obj) },
};
STATIC MP_DEFINE_CONST_DICT(pitch_yin_locals_dict, pitch_yin_locals_dict_table);

/* DECLARE THE MODULE TYPE */
const mp_obj_type_t pitch_yin_type = {
    { &mp_type_type },
    .name = MP_QSTR_Yin,
    .make_new = pitch_yin_make_new,
    .locals_dict = (mp_obj_dict_t*)&pitch_yin_locals_dict,
};
