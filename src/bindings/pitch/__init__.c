#include <stdint.h>
#include <stdlib.h>

#include "py/obj.h"
#include "py/runtime.h"

#include "shared-bindings/pitch/__init__.h"
#include "shared-bindings/pitch/Yin.h"

STATIC const mp_rom_map_elem_t pitch_module_globals_table[] = {
	{ 
		MP_ROM_QSTR(MP_QSTR___name__), 
		MP_ROM_QSTR(MP_QSTR_pitch) 
	},
	{ 
		MP_ROM_QSTR(MP_QSTR_Yin), 
		MP_ROM_PTR(&pitch_yin_type) 
	},
};

STATIC MP_DEFINE_CONST_DICT(
	pitch_module_globals, 
	pitch_module_globals_table
);

const mp_obj_module_t pitch_module = {
	.base		= { &mp_type_module },
	.globals	= (mp_obj_dict_t*)&pitch_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_pitch, pitch_module, 1);