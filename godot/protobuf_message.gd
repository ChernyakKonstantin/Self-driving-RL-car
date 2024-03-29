const PROTO_VERSION = 3

#
# BSD 3-Clause License
#
# Copyright (c) 2018 - 2022, Oleg Malyavkin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# DEBUG_TAB redefine this "  " if you need, example: const DEBUG_TAB = "\t"
const DEBUG_TAB : String = "  "

enum PB_ERR {
	NO_ERRORS = 0,
	VARINT_NOT_FOUND = -1,
	REPEATED_COUNT_NOT_FOUND = -2,
	REPEATED_COUNT_MISMATCH = -3,
	LENGTHDEL_SIZE_NOT_FOUND = -4,
	LENGTHDEL_SIZE_MISMATCH = -5,
	PACKAGE_SIZE_MISMATCH = -6,
	UNDEFINED_STATE = -7,
	PARSE_INCOMPLETE = -8,
	REQUIRED_FIELDS = -9
}

enum PB_DATA_TYPE {
	INT32 = 0,
	SINT32 = 1,
	UINT32 = 2,
	INT64 = 3,
	SINT64 = 4,
	UINT64 = 5,
	BOOL = 6,
	ENUM = 7,
	FIXED32 = 8,
	SFIXED32 = 9,
	FLOAT = 10,
	FIXED64 = 11,
	SFIXED64 = 12,
	DOUBLE = 13,
	STRING = 14,
	BYTES = 15,
	MESSAGE = 16,
	MAP = 17
}

const DEFAULT_VALUES_2 = {
	PB_DATA_TYPE.INT32: null,
	PB_DATA_TYPE.SINT32: null,
	PB_DATA_TYPE.UINT32: null,
	PB_DATA_TYPE.INT64: null,
	PB_DATA_TYPE.SINT64: null,
	PB_DATA_TYPE.UINT64: null,
	PB_DATA_TYPE.BOOL: null,
	PB_DATA_TYPE.ENUM: null,
	PB_DATA_TYPE.FIXED32: null,
	PB_DATA_TYPE.SFIXED32: null,
	PB_DATA_TYPE.FLOAT: null,
	PB_DATA_TYPE.FIXED64: null,
	PB_DATA_TYPE.SFIXED64: null,
	PB_DATA_TYPE.DOUBLE: null,
	PB_DATA_TYPE.STRING: null,
	PB_DATA_TYPE.BYTES: null,
	PB_DATA_TYPE.MESSAGE: null,
	PB_DATA_TYPE.MAP: null
}

const DEFAULT_VALUES_3 = {
	PB_DATA_TYPE.INT32: 0,
	PB_DATA_TYPE.SINT32: 0,
	PB_DATA_TYPE.UINT32: 0,
	PB_DATA_TYPE.INT64: 0,
	PB_DATA_TYPE.SINT64: 0,
	PB_DATA_TYPE.UINT64: 0,
	PB_DATA_TYPE.BOOL: false,
	PB_DATA_TYPE.ENUM: 0,
	PB_DATA_TYPE.FIXED32: 0,
	PB_DATA_TYPE.SFIXED32: 0,
	PB_DATA_TYPE.FLOAT: 0.0,
	PB_DATA_TYPE.FIXED64: 0,
	PB_DATA_TYPE.SFIXED64: 0,
	PB_DATA_TYPE.DOUBLE: 0.0,
	PB_DATA_TYPE.STRING: "",
	PB_DATA_TYPE.BYTES: [],
	PB_DATA_TYPE.MESSAGE: null,
	PB_DATA_TYPE.MAP: []
}

enum PB_TYPE {
	VARINT = 0,
	FIX64 = 1,
	LENGTHDEL = 2,
	STARTGROUP = 3,
	ENDGROUP = 4,
	FIX32 = 5,
	UNDEFINED = 8
}

enum PB_RULE {
	OPTIONAL = 0,
	REQUIRED = 1,
	REPEATED = 2,
	RESERVED = 3
}

enum PB_SERVICE_STATE {
	FILLED = 0,
	UNFILLED = 1
}

class PBField:
	func _init(a_name : String, a_type : int, a_rule : int, a_tag : int, packed : bool, a_value = null):
		name = a_name
		type = a_type
		rule = a_rule
		tag = a_tag
		option_packed = packed
		value = a_value
		
	var name : String
	var type : int
	var rule : int
	var tag : int
	var option_packed : bool
	var value
	var is_map_field : bool = false
	var option_default : bool = false

class PBTypeTag:
	var ok : bool = false
	var type : int
	var tag : int
	var offset : int

class PBServiceField:
	var field : PBField
	var func_ref = null
	var state : int = PB_SERVICE_STATE.UNFILLED

class PBPacker:
	static func convert_signed(n : int) -> int:
		if n < -2147483648:
			return (n << 1) ^ (n >> 63)
		else:
			return (n << 1) ^ (n >> 31)

	static func deconvert_signed(n : int) -> int:
		if n & 0x01:
			return ~(n >> 1)
		else:
			return (n >> 1)

	static func pack_varint(value) -> PoolByteArray:
		var varint : PoolByteArray = PoolByteArray()
		if typeof(value) == TYPE_BOOL:
			if value:
				value = 1
			else:
				value = 0
		for _i in range(9):
			var b = value & 0x7F
			value >>= 7
			if value:
				varint.append(b | 0x80)
			else:
				varint.append(b)
				break
		if varint.size() == 9 && varint[8] == 0xFF:
			varint.append(0x01)
		return varint

	static func pack_bytes(value, count : int, data_type : int) -> PoolByteArray:
		var bytes : PoolByteArray = PoolByteArray()
		if data_type == PB_DATA_TYPE.FLOAT:
			var spb : StreamPeerBuffer = StreamPeerBuffer.new()
			spb.put_float(value)
			bytes = spb.get_data_array()
		elif data_type == PB_DATA_TYPE.DOUBLE:
			var spb : StreamPeerBuffer = StreamPeerBuffer.new()
			spb.put_double(value)
			bytes = spb.get_data_array()
		else:
			for _i in range(count):
				bytes.append(value & 0xFF)
				value >>= 8
		return bytes

	static func unpack_bytes(bytes : PoolByteArray, index : int, count : int, data_type : int):
		var value = 0
		if data_type == PB_DATA_TYPE.FLOAT:
			var spb : StreamPeerBuffer = StreamPeerBuffer.new()
			for i in range(index, count + index):
				spb.put_u8(bytes[i])
			spb.seek(0)
			value = spb.get_float()
		elif data_type == PB_DATA_TYPE.DOUBLE:
			var spb : StreamPeerBuffer = StreamPeerBuffer.new()
			for i in range(index, count + index):
				spb.put_u8(bytes[i])
			spb.seek(0)
			value = spb.get_double()
		else:
			for i in range(index + count - 1, index - 1, -1):
				value |= (bytes[i] & 0xFF)
				if i != index:
					value <<= 8
		return value

	static func unpack_varint(varint_bytes) -> int:
		var value : int = 0
		for i in range(varint_bytes.size() - 1, -1, -1):
			value |= varint_bytes[i] & 0x7F
			if i != 0:
				value <<= 7
		return value

	static func pack_type_tag(type : int, tag : int) -> PoolByteArray:
		return pack_varint((tag << 3) | type)

	static func isolate_varint(bytes : PoolByteArray, index : int) -> PoolByteArray:
		var result : PoolByteArray = PoolByteArray()
		for i in range(index, bytes.size()):
			result.append(bytes[i])
			if !(bytes[i] & 0x80):
				break
		return result

	static func unpack_type_tag(bytes : PoolByteArray, index : int) -> PBTypeTag:
		var varint_bytes : PoolByteArray = isolate_varint(bytes, index)
		var result : PBTypeTag = PBTypeTag.new()
		if varint_bytes.size() != 0:
			result.ok = true
			result.offset = varint_bytes.size()
			var unpacked : int = unpack_varint(varint_bytes)
			result.type = unpacked & 0x07
			result.tag = unpacked >> 3
		return result

	static func pack_length_delimeted(type : int, tag : int, bytes : PoolByteArray) -> PoolByteArray:
		var result : PoolByteArray = pack_type_tag(type, tag)
		result.append_array(pack_varint(bytes.size()))
		result.append_array(bytes)
		return result

	static func pb_type_from_data_type(data_type : int) -> int:
		if data_type == PB_DATA_TYPE.INT32 || data_type == PB_DATA_TYPE.SINT32 || data_type == PB_DATA_TYPE.UINT32 || data_type == PB_DATA_TYPE.INT64 || data_type == PB_DATA_TYPE.SINT64 || data_type == PB_DATA_TYPE.UINT64 || data_type == PB_DATA_TYPE.BOOL || data_type == PB_DATA_TYPE.ENUM:
			return PB_TYPE.VARINT
		elif data_type == PB_DATA_TYPE.FIXED32 || data_type == PB_DATA_TYPE.SFIXED32 || data_type == PB_DATA_TYPE.FLOAT:
			return PB_TYPE.FIX32
		elif data_type == PB_DATA_TYPE.FIXED64 || data_type == PB_DATA_TYPE.SFIXED64 || data_type == PB_DATA_TYPE.DOUBLE:
			return PB_TYPE.FIX64
		elif data_type == PB_DATA_TYPE.STRING || data_type == PB_DATA_TYPE.BYTES || data_type == PB_DATA_TYPE.MESSAGE || data_type == PB_DATA_TYPE.MAP:
			return PB_TYPE.LENGTHDEL
		else:
			return PB_TYPE.UNDEFINED

	static func pack_field(field : PBField) -> PoolByteArray:
		var type : int = pb_type_from_data_type(field.type)
		var type_copy : int = type
		if field.rule == PB_RULE.REPEATED && field.option_packed:
			type = PB_TYPE.LENGTHDEL
		var head : PoolByteArray = pack_type_tag(type, field.tag)
		var data : PoolByteArray = PoolByteArray()
		if type == PB_TYPE.VARINT:
			var value
			if field.rule == PB_RULE.REPEATED:
				for v in field.value:
					data.append_array(head)
					if field.type == PB_DATA_TYPE.SINT32 || field.type == PB_DATA_TYPE.SINT64:
						value = convert_signed(v)
					else:
						value = v
					data.append_array(pack_varint(value))
				return data
			else:
				if field.type == PB_DATA_TYPE.SINT32 || field.type == PB_DATA_TYPE.SINT64:
					value = convert_signed(field.value)
				else:
					value = field.value
				data = pack_varint(value)
		elif type == PB_TYPE.FIX32:
			if field.rule == PB_RULE.REPEATED:
				for v in field.value:
					data.append_array(head)
					data.append_array(pack_bytes(v, 4, field.type))
				return data
			else:
				data.append_array(pack_bytes(field.value, 4, field.type))
		elif type == PB_TYPE.FIX64:
			if field.rule == PB_RULE.REPEATED:
				for v in field.value:
					data.append_array(head)
					data.append_array(pack_bytes(v, 8, field.type))
				return data
			else:
				data.append_array(pack_bytes(field.value, 8, field.type))
		elif type == PB_TYPE.LENGTHDEL:
			if field.rule == PB_RULE.REPEATED:
				if type_copy == PB_TYPE.VARINT:
					if field.type == PB_DATA_TYPE.SINT32 || field.type == PB_DATA_TYPE.SINT64:
						var signed_value : int
						for v in field.value:
							signed_value = convert_signed(v)
							data.append_array(pack_varint(signed_value))
					else:
						for v in field.value:
							data.append_array(pack_varint(v))
					return pack_length_delimeted(type, field.tag, data)
				elif type_copy == PB_TYPE.FIX32:
					for v in field.value:
						data.append_array(pack_bytes(v, 4, field.type))
					return pack_length_delimeted(type, field.tag, data)
				elif type_copy == PB_TYPE.FIX64:
					for v in field.value:
						data.append_array(pack_bytes(v, 8, field.type))
					return pack_length_delimeted(type, field.tag, data)
				elif field.type == PB_DATA_TYPE.STRING:
					for v in field.value:
						var obj = v.to_utf8()
						data.append_array(pack_length_delimeted(type, field.tag, obj))
					return data
				elif field.type == PB_DATA_TYPE.BYTES:
					for v in field.value:
						data.append_array(pack_length_delimeted(type, field.tag, v))
					return data
				elif typeof(field.value[0]) == TYPE_OBJECT:
					for v in field.value:
						var obj : PoolByteArray = v.to_bytes()
						data.append_array(pack_length_delimeted(type, field.tag, obj))
					return data
			else:
				if field.type == PB_DATA_TYPE.STRING:
					var str_bytes : PoolByteArray = field.value.to_utf8()
					if PROTO_VERSION == 2 || (PROTO_VERSION == 3 && str_bytes.size() > 0):
						data.append_array(str_bytes)
						return pack_length_delimeted(type, field.tag, data)
				if field.type == PB_DATA_TYPE.BYTES:
					if PROTO_VERSION == 2 || (PROTO_VERSION == 3 && field.value.size() > 0):
						data.append_array(field.value)
						return pack_length_delimeted(type, field.tag, data)
				elif typeof(field.value) == TYPE_OBJECT:
					var obj : PoolByteArray = field.value.to_bytes()
					if obj.size() > 0:
						data.append_array(obj)
					return pack_length_delimeted(type, field.tag, data)
				else:
					pass
		if data.size() > 0:
			head.append_array(data)
			return head
		else:
			return data

	static func unpack_field(bytes : PoolByteArray, offset : int, field : PBField, type : int, message_func_ref) -> int:
		if field.rule == PB_RULE.REPEATED && type != PB_TYPE.LENGTHDEL && field.option_packed:
			var count = isolate_varint(bytes, offset)
			if count.size() > 0:
				offset += count.size()
				count = unpack_varint(count)
				if type == PB_TYPE.VARINT:
					var val
					var counter = offset + count
					while offset < counter:
						val = isolate_varint(bytes, offset)
						if val.size() > 0:
							offset += val.size()
							val = unpack_varint(val)
							if field.type == PB_DATA_TYPE.SINT32 || field.type == PB_DATA_TYPE.SINT64:
								val = deconvert_signed(val)
							elif field.type == PB_DATA_TYPE.BOOL:
								if val:
									val = true
								else:
									val = false
							field.value.append(val)
						else:
							return PB_ERR.REPEATED_COUNT_MISMATCH
					return offset
				elif type == PB_TYPE.FIX32 || type == PB_TYPE.FIX64:
					var type_size
					if type == PB_TYPE.FIX32:
						type_size = 4
					else:
						type_size = 8
					var val
					var counter = offset + count
					while offset < counter:
						if (offset + type_size) > bytes.size():
							return PB_ERR.REPEATED_COUNT_MISMATCH
						val = unpack_bytes(bytes, offset, type_size, field.type)
						offset += type_size
						field.value.append(val)
					return offset
			else:
				return PB_ERR.REPEATED_COUNT_NOT_FOUND
		else:
			if type == PB_TYPE.VARINT:
				var val = isolate_varint(bytes, offset)
				if val.size() > 0:
					offset += val.size()
					val = unpack_varint(val)
					if field.type == PB_DATA_TYPE.SINT32 || field.type == PB_DATA_TYPE.SINT64:
						val = deconvert_signed(val)
					elif field.type == PB_DATA_TYPE.BOOL:
						if val:
							val = true
						else:
							val = false
					if field.rule == PB_RULE.REPEATED:
						field.value.append(val)
					else:
						field.value = val
				else:
					return PB_ERR.VARINT_NOT_FOUND
				return offset
			elif type == PB_TYPE.FIX32 || type == PB_TYPE.FIX64:
				var type_size
				if type == PB_TYPE.FIX32:
					type_size = 4
				else:
					type_size = 8
				var val
				if (offset + type_size) > bytes.size():
					return PB_ERR.REPEATED_COUNT_MISMATCH
				val = unpack_bytes(bytes, offset, type_size, field.type)
				offset += type_size
				if field.rule == PB_RULE.REPEATED:
					field.value.append(val)
				else:
					field.value = val
				return offset
			elif type == PB_TYPE.LENGTHDEL:
				var inner_size = isolate_varint(bytes, offset)
				if inner_size.size() > 0:
					offset += inner_size.size()
					inner_size = unpack_varint(inner_size)
					if inner_size >= 0:
						if inner_size + offset > bytes.size():
							return PB_ERR.LENGTHDEL_SIZE_MISMATCH
						if message_func_ref != null:
							var message = message_func_ref.call_func()
							if inner_size > 0:
								var sub_offset = message.from_bytes(bytes, offset, inner_size + offset)
								if sub_offset > 0:
									if sub_offset - offset >= inner_size:
										offset = sub_offset
										return offset
									else:
										return PB_ERR.LENGTHDEL_SIZE_MISMATCH
								return sub_offset
							else:
								return offset
						elif field.type == PB_DATA_TYPE.STRING:
							var str_bytes : PoolByteArray = PoolByteArray()
							for i in range(offset, inner_size + offset):
								str_bytes.append(bytes[i])
							if field.rule == PB_RULE.REPEATED:
								field.value.append(str_bytes.get_string_from_utf8())
							else:
								field.value = str_bytes.get_string_from_utf8()
							return offset + inner_size
						elif field.type == PB_DATA_TYPE.BYTES:
							var val_bytes : PoolByteArray = PoolByteArray()
							for i in range(offset, inner_size + offset):
								val_bytes.append(bytes[i])
							if field.rule == PB_RULE.REPEATED:
								field.value.append(val_bytes)
							else:
								field.value = val_bytes
							return offset + inner_size
					else:
						return PB_ERR.LENGTHDEL_SIZE_NOT_FOUND
				else:
					return PB_ERR.LENGTHDEL_SIZE_NOT_FOUND
		return PB_ERR.UNDEFINED_STATE

	static func unpack_message(data, bytes : PoolByteArray, offset : int, limit : int) -> int:
		while true:
			var tt : PBTypeTag = unpack_type_tag(bytes, offset)
			if tt.ok:
				offset += tt.offset
				if data.has(tt.tag):
					var service : PBServiceField = data[tt.tag]
					var type : int = pb_type_from_data_type(service.field.type)
					if type == tt.type || (tt.type == PB_TYPE.LENGTHDEL && service.field.rule == PB_RULE.REPEATED && service.field.option_packed):
						var res : int = unpack_field(bytes, offset, service.field, type, service.func_ref)
						if res > 0:
							service.state = PB_SERVICE_STATE.FILLED
							offset = res
							if offset == limit:
								return offset
							elif offset > limit:
								return PB_ERR.PACKAGE_SIZE_MISMATCH
						elif res < 0:
							return res
						else:
							break
			else:
				return offset
		return PB_ERR.UNDEFINED_STATE

	static func pack_message(data) -> PoolByteArray:
		var DEFAULT_VALUES
		if PROTO_VERSION == 2:
			DEFAULT_VALUES = DEFAULT_VALUES_2
		elif PROTO_VERSION == 3:
			DEFAULT_VALUES = DEFAULT_VALUES_3
		var result : PoolByteArray = PoolByteArray()
		var keys : Array = data.keys()
		keys.sort()
		for i in keys:
			if data[i].field.value != null:
				if data[i].state == PB_SERVICE_STATE.UNFILLED \
				&& !data[i].field.is_map_field \
				&& typeof(data[i].field.value) == typeof(DEFAULT_VALUES[data[i].field.type]) \
				&& data[i].field.value == DEFAULT_VALUES[data[i].field.type]:
					continue
				elif data[i].field.rule == PB_RULE.REPEATED && data[i].field.value.size() == 0:
					continue
				result.append_array(pack_field(data[i].field))
			elif data[i].field.rule == PB_RULE.REQUIRED:
				print("Error: required field is not filled: Tag:", data[i].field.tag)
				return PoolByteArray()
		return result

	static func check_required(data) -> bool:
		var keys : Array = data.keys()
		for i in keys:
			if data[i].field.rule == PB_RULE.REQUIRED && data[i].state == PB_SERVICE_STATE.UNFILLED:
				return false
		return true

	static func construct_map(key_values):
		var result = {}
		for kv in key_values:
			result[kv.get_key()] = kv.get_value()
		return result
	
	static func tabulate(text : String, nesting : int) -> String:
		var tab : String = ""
		for _i in range(nesting):
			tab += DEBUG_TAB
		return tab + text
	
	static func value_to_string(value, field : PBField, nesting : int) -> String:
		var result : String = ""
		var text : String
		if field.type == PB_DATA_TYPE.MESSAGE:
			result += "{"
			nesting += 1
			text = message_to_string(value.data, nesting)
			if text != "":
				result += "\n" + text
				nesting -= 1
				result += tabulate("}", nesting)
			else:
				nesting -= 1
				result += "}"
		elif field.type == PB_DATA_TYPE.BYTES:
			result += "<"
			for i in range(value.size()):
				result += String(value[i])
				if i != (value.size() - 1):
					result += ", "
			result += ">"
		elif field.type == PB_DATA_TYPE.STRING:
			result += "\"" + value + "\""
		elif field.type == PB_DATA_TYPE.ENUM:
			result += "ENUM::" + String(value)
		else:
			result += String(value)
		return result
	
	static func field_to_string(field : PBField, nesting : int) -> String:
		var result : String = tabulate(field.name + ": ", nesting)
		if field.type == PB_DATA_TYPE.MAP:
			if field.value.size() > 0:
				result += "(\n"
				nesting += 1
				for i in range(field.value.size()):
					var local_key_value = field.value[i].data[1].field
					result += tabulate(value_to_string(local_key_value.value, local_key_value, nesting), nesting) + ": "
					local_key_value = field.value[i].data[2].field
					result += value_to_string(local_key_value.value, local_key_value, nesting)
					if i != (field.value.size() - 1):
						result += ","
					result += "\n"
				nesting -= 1
				result += tabulate(")", nesting)
			else:
				result += "()"
		elif field.rule == PB_RULE.REPEATED:
			if field.value.size() > 0:
				result += "[\n"
				nesting += 1
				for i in range(field.value.size()):
					result += tabulate(String(i) + ": ", nesting)
					result += value_to_string(field.value[i], field, nesting)
					if i != (field.value.size() - 1):
						result += ","
					result += "\n"
				nesting -= 1
				result += tabulate("]", nesting)
			else:
				result += "[]"
		else:
			result += value_to_string(field.value, field, nesting)
		result += ";\n"
		return result
		
	static func message_to_string(data, nesting : int = 0) -> String:
		var DEFAULT_VALUES
		if PROTO_VERSION == 2:
			DEFAULT_VALUES = DEFAULT_VALUES_2
		elif PROTO_VERSION == 3:
			DEFAULT_VALUES = DEFAULT_VALUES_3
		var result : String = ""
		var keys : Array = data.keys()
		keys.sort()
		for i in keys:
			if data[i].field.value != null:
				if data[i].state == PB_SERVICE_STATE.UNFILLED \
				&& !data[i].field.is_map_field \
				&& typeof(data[i].field.value) == typeof(DEFAULT_VALUES[data[i].field.type]) \
				&& data[i].field.value == DEFAULT_VALUES[data[i].field.type]:
					continue
				elif data[i].field.rule == PB_RULE.REPEATED && data[i].field.value.size() == 0:
					continue
				result += field_to_string(data[i].field, nesting)
			elif data[i].field.rule == PB_RULE.REQUIRED:
				result += data[i].field.name + ": " + "error"
		return result



############### USER DATA BEGIN ################


class WorldData:
	func _init():
		var service
		
	var data = {}
	
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
class Point3D:
	func _init():
		var service
		
		_x = PBField.new("x", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 1, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _x
		data[_x.tag] = service
		
		_y = PBField.new("y", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 2, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _y
		data[_y.tag] = service
		
		_z = PBField.new("z", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 3, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _z
		data[_z.tag] = service
		
		_rot_x = PBField.new("rot_x", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 4, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _rot_x
		data[_rot_x.tag] = service
		
		_rot_y = PBField.new("rot_y", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 5, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _rot_y
		data[_rot_y.tag] = service
		
		_rot_z = PBField.new("rot_z", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 6, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _rot_z
		data[_rot_z.tag] = service
		
	var data = {}
	
	var _x: PBField
	func get_x() -> float:
		return _x.value
	func clear_x() -> void:
		data[1].state = PB_SERVICE_STATE.UNFILLED
		_x.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_x(value : float) -> void:
		_x.value = value
	
	var _y: PBField
	func get_y() -> float:
		return _y.value
	func clear_y() -> void:
		data[2].state = PB_SERVICE_STATE.UNFILLED
		_y.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_y(value : float) -> void:
		_y.value = value
	
	var _z: PBField
	func get_z() -> float:
		return _z.value
	func clear_z() -> void:
		data[3].state = PB_SERVICE_STATE.UNFILLED
		_z.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_z(value : float) -> void:
		_z.value = value
	
	var _rot_x: PBField
	func get_rot_x() -> float:
		return _rot_x.value
	func clear_rot_x() -> void:
		data[4].state = PB_SERVICE_STATE.UNFILLED
		_rot_x.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_rot_x(value : float) -> void:
		_rot_x.value = value
	
	var _rot_y: PBField
	func get_rot_y() -> float:
		return _rot_y.value
	func clear_rot_y() -> void:
		data[5].state = PB_SERVICE_STATE.UNFILLED
		_rot_y.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_rot_y(value : float) -> void:
		_rot_y.value = value
	
	var _rot_z: PBField
	func get_rot_z() -> float:
		return _rot_z.value
	func clear_rot_z() -> void:
		data[6].state = PB_SERVICE_STATE.UNFILLED
		_rot_z.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_rot_z(value : float) -> void:
		_rot_z.value = value
	
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
class CameraFrame:
	func _init():
		var service
		
		_height = PBField.new("height", PB_DATA_TYPE.INT32, PB_RULE.OPTIONAL, 1, true, DEFAULT_VALUES_3[PB_DATA_TYPE.INT32])
		service = PBServiceField.new()
		service.field = _height
		data[_height.tag] = service
		
		_width = PBField.new("width", PB_DATA_TYPE.INT32, PB_RULE.OPTIONAL, 2, true, DEFAULT_VALUES_3[PB_DATA_TYPE.INT32])
		service = PBServiceField.new()
		service.field = _width
		data[_width.tag] = service
		
		_format = PBField.new("format", PB_DATA_TYPE.STRING, PB_RULE.OPTIONAL, 3, true, DEFAULT_VALUES_3[PB_DATA_TYPE.STRING])
		service = PBServiceField.new()
		service.field = _format
		data[_format.tag] = service
		
		_data = PBField.new("data", PB_DATA_TYPE.BYTES, PB_RULE.OPTIONAL, 4, true, DEFAULT_VALUES_3[PB_DATA_TYPE.BYTES])
		service = PBServiceField.new()
		service.field = _data
		data[_data.tag] = service
		
	var data = {}
	
	var _height: PBField
	func get_height() -> int:
		return _height.value
	func clear_height() -> void:
		data[1].state = PB_SERVICE_STATE.UNFILLED
		_height.value = DEFAULT_VALUES_3[PB_DATA_TYPE.INT32]
	func set_height(value : int) -> void:
		_height.value = value
	
	var _width: PBField
	func get_width() -> int:
		return _width.value
	func clear_width() -> void:
		data[2].state = PB_SERVICE_STATE.UNFILLED
		_width.value = DEFAULT_VALUES_3[PB_DATA_TYPE.INT32]
	func set_width(value : int) -> void:
		_width.value = value
	
	var _format: PBField
	func get_format() -> String:
		return _format.value
	func clear_format() -> void:
		data[3].state = PB_SERVICE_STATE.UNFILLED
		_format.value = DEFAULT_VALUES_3[PB_DATA_TYPE.STRING]
	func set_format(value : String) -> void:
		_format.value = value
	
	var _data: PBField
	func get_data() -> PoolByteArray:
		return _data.value
	func clear_data() -> void:
		data[4].state = PB_SERVICE_STATE.UNFILLED
		_data.value = DEFAULT_VALUES_3[PB_DATA_TYPE.BYTES]
	func set_data(value : PoolByteArray) -> void:
		_data.value = value
	
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
class CameraFrames:
	func _init():
		var service
		
		_frame = PBField.new("frame", PB_DATA_TYPE.MESSAGE, PB_RULE.REPEATED, 1, true, [])
		service = PBServiceField.new()
		service.field = _frame
		service.func_ref = funcref(self, "add_frame")
		data[_frame.tag] = service
		
	var data = {}
	
	var _frame: PBField
	func get_frame() -> Array:
		return _frame.value
	func clear_frame() -> void:
		data[1].state = PB_SERVICE_STATE.UNFILLED
		_frame.value = []
	func add_frame() -> CameraFrame:
		var element = CameraFrame.new()
		_frame.value.append(element)
		return element
	
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
class ParkingSensorDistances:
	func _init():
		var service
		
		_distance = PBField.new("distance", PB_DATA_TYPE.FLOAT, PB_RULE.REPEATED, 1, true, [])
		service = PBServiceField.new()
		service.field = _distance
		data[_distance.tag] = service
		
	var data = {}
	
	var _distance: PBField
	func get_distance() -> Array:
		return _distance.value
	func clear_distance() -> void:
		data[1].state = PB_SERVICE_STATE.UNFILLED
		_distance.value = []
	func add_distance(value : float) -> void:
		_distance.value.append(value)
	
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
class Points3D:
	func _init():
		var service
		
		_point = PBField.new("point", PB_DATA_TYPE.MESSAGE, PB_RULE.REPEATED, 1, true, [])
		service = PBServiceField.new()
		service.field = _point
		service.func_ref = funcref(self, "add_point")
		data[_point.tag] = service
		
	var data = {}
	
	var _point: PBField
	func get_point() -> Array:
		return _point.value
	func clear_point() -> void:
		data[1].state = PB_SERVICE_STATE.UNFILLED
		_point.value = []
	func add_point() -> Point3D:
		var element = Point3D.new()
		_point.value.append(element)
		return element
	
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
class AgentData:
	func _init():
		var service
		
		_is_crashed = PBField.new("is_crashed", PB_DATA_TYPE.BOOL, PB_RULE.OPTIONAL, 1, true, DEFAULT_VALUES_3[PB_DATA_TYPE.BOOL])
		service = PBServiceField.new()
		service.field = _is_crashed
		data[_is_crashed.tag] = service
		
		_steering = PBField.new("steering", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 2, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _steering
		data[_steering.tag] = service
		
		_speed = PBField.new("speed", PB_DATA_TYPE.FLOAT, PB_RULE.OPTIONAL, 3, true, DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT])
		service = PBServiceField.new()
		service.field = _speed
		data[_speed.tag] = service
		
		_lidar = PBField.new("lidar", PB_DATA_TYPE.MESSAGE, PB_RULE.REPEATED, 4, true, [])
		service = PBServiceField.new()
		service.field = _lidar
		service.func_ref = funcref(self, "add_lidar")
		data[_lidar.tag] = service
		
		_cameras = PBField.new("cameras", PB_DATA_TYPE.MAP, PB_RULE.REPEATED, 5, true, [])
		service = PBServiceField.new()
		service.field = _cameras
		service.func_ref = funcref(self, "add_empty_cameras")
		data[_cameras.tag] = service
		
		_parking_sensors = PBField.new("parking_sensors", PB_DATA_TYPE.MAP, PB_RULE.REPEATED, 6, true, [])
		service = PBServiceField.new()
		service.field = _parking_sensors
		service.func_ref = funcref(self, "add_empty_parking_sensors")
		data[_parking_sensors.tag] = service
		
		_global_coordinates = PBField.new("global_coordinates", PB_DATA_TYPE.MESSAGE, PB_RULE.OPTIONAL, 7, true, DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE])
		service = PBServiceField.new()
		service.field = _global_coordinates
		service.func_ref = funcref(self, "new_global_coordinates")
		data[_global_coordinates.tag] = service
		
	var data = {}
	
	var _is_crashed: PBField
	func get_is_crashed() -> bool:
		return _is_crashed.value
	func clear_is_crashed() -> void:
		data[1].state = PB_SERVICE_STATE.UNFILLED
		_is_crashed.value = DEFAULT_VALUES_3[PB_DATA_TYPE.BOOL]
	func set_is_crashed(value : bool) -> void:
		_is_crashed.value = value
	
	var _steering: PBField
	func get_steering() -> float:
		return _steering.value
	func clear_steering() -> void:
		data[2].state = PB_SERVICE_STATE.UNFILLED
		_steering.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_steering(value : float) -> void:
		_steering.value = value
	
	var _speed: PBField
	func get_speed() -> float:
		return _speed.value
	func clear_speed() -> void:
		data[3].state = PB_SERVICE_STATE.UNFILLED
		_speed.value = DEFAULT_VALUES_3[PB_DATA_TYPE.FLOAT]
	func set_speed(value : float) -> void:
		_speed.value = value
	
	var _lidar: PBField
	func get_lidar() -> Array:
		return _lidar.value
	func clear_lidar() -> void:
		data[4].state = PB_SERVICE_STATE.UNFILLED
		_lidar.value = []
	func add_lidar() -> Points3D:
		var element = Points3D.new()
		_lidar.value.append(element)
		return element
	
	var _cameras: PBField
	func get_raw_cameras():
		return _cameras.value
	func get_cameras():
		return PBPacker.construct_map(_cameras.value)
	func clear_cameras():
		data[5].state = PB_SERVICE_STATE.UNFILLED
		_cameras.value = DEFAULT_VALUES_3[PB_DATA_TYPE.MAP]
	func add_empty_cameras() -> AgentData.map_type_cameras:
		var element = AgentData.map_type_cameras.new()
		_cameras.value.append(element)
		return element
	func add_cameras(a_key) -> AgentData.map_type_cameras:
		var idx = -1
		for i in range(_cameras.value.size()):
			if _cameras.value[i].get_key() == a_key:
				idx = i
				break
		var element = AgentData.map_type_cameras.new()
		element.set_key(a_key)
		if idx != -1:
			_cameras.value[idx] = element
		else:
			_cameras.value.append(element)
		return element.new_value()
	
	var _parking_sensors: PBField
	func get_raw_parking_sensors():
		return _parking_sensors.value
	func get_parking_sensors():
		return PBPacker.construct_map(_parking_sensors.value)
	func clear_parking_sensors():
		data[6].state = PB_SERVICE_STATE.UNFILLED
		_parking_sensors.value = DEFAULT_VALUES_3[PB_DATA_TYPE.MAP]
	func add_empty_parking_sensors() -> AgentData.map_type_parking_sensors:
		var element = AgentData.map_type_parking_sensors.new()
		_parking_sensors.value.append(element)
		return element
	func add_parking_sensors(a_key) -> AgentData.map_type_parking_sensors:
		var idx = -1
		for i in range(_parking_sensors.value.size()):
			if _parking_sensors.value[i].get_key() == a_key:
				idx = i
				break
		var element = AgentData.map_type_parking_sensors.new()
		element.set_key(a_key)
		if idx != -1:
			_parking_sensors.value[idx] = element
		else:
			_parking_sensors.value.append(element)
		return element.new_value()
	
	var _global_coordinates: PBField
	func get_global_coordinates() -> Point3D:
		return _global_coordinates.value
	func clear_global_coordinates() -> void:
		data[7].state = PB_SERVICE_STATE.UNFILLED
		_global_coordinates.value = DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE]
	func new_global_coordinates() -> Point3D:
		_global_coordinates.value = Point3D.new()
		return _global_coordinates.value
	
	class map_type_cameras:
		func _init():
			var service
			
			_key = PBField.new("key", PB_DATA_TYPE.STRING, PB_RULE.REQUIRED, 1, true, DEFAULT_VALUES_3[PB_DATA_TYPE.STRING])
			_key.is_map_field = true
			service = PBServiceField.new()
			service.field = _key
			data[_key.tag] = service
			
			_value = PBField.new("value", PB_DATA_TYPE.MESSAGE, PB_RULE.REQUIRED, 2, true, DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE])
			_value.is_map_field = true
			service = PBServiceField.new()
			service.field = _value
			service.func_ref = funcref(self, "new_value")
			data[_value.tag] = service
			
		var data = {}
		
		var _key: PBField
		func get_key() -> String:
			return _key.value
		func clear_key() -> void:
			data[1].state = PB_SERVICE_STATE.UNFILLED
			_key.value = DEFAULT_VALUES_3[PB_DATA_TYPE.STRING]
		func set_key(value : String) -> void:
			_key.value = value
		
		var _value: PBField
		func get_value() -> CameraFrames:
			return _value.value
		func clear_value() -> void:
			data[2].state = PB_SERVICE_STATE.UNFILLED
			_value.value = DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE]
		func new_value() -> CameraFrames:
			_value.value = CameraFrames.new()
			return _value.value
		
		func to_string() -> String:
			return PBPacker.message_to_string(data)
			
		func to_bytes() -> PoolByteArray:
			return PBPacker.pack_message(data)
			
		func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
			var cur_limit = bytes.size()
			if limit != -1:
				cur_limit = limit
			var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
			if result == cur_limit:
				if PBPacker.check_required(data):
					if limit == -1:
						return PB_ERR.NO_ERRORS
				else:
					return PB_ERR.REQUIRED_FIELDS
			elif limit == -1 && result > 0:
				return PB_ERR.PARSE_INCOMPLETE
			return result
		
	class map_type_parking_sensors:
		func _init():
			var service
			
			_key = PBField.new("key", PB_DATA_TYPE.STRING, PB_RULE.REQUIRED, 1, true, DEFAULT_VALUES_3[PB_DATA_TYPE.STRING])
			_key.is_map_field = true
			service = PBServiceField.new()
			service.field = _key
			data[_key.tag] = service
			
			_value = PBField.new("value", PB_DATA_TYPE.MESSAGE, PB_RULE.REQUIRED, 2, true, DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE])
			_value.is_map_field = true
			service = PBServiceField.new()
			service.field = _value
			service.func_ref = funcref(self, "new_value")
			data[_value.tag] = service
			
		var data = {}
		
		var _key: PBField
		func get_key() -> String:
			return _key.value
		func clear_key() -> void:
			data[1].state = PB_SERVICE_STATE.UNFILLED
			_key.value = DEFAULT_VALUES_3[PB_DATA_TYPE.STRING]
		func set_key(value : String) -> void:
			_key.value = value
		
		var _value: PBField
		func get_value() -> ParkingSensorDistances:
			return _value.value
		func clear_value() -> void:
			data[2].state = PB_SERVICE_STATE.UNFILLED
			_value.value = DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE]
		func new_value() -> ParkingSensorDistances:
			_value.value = ParkingSensorDistances.new()
			return _value.value
		
		func to_string() -> String:
			return PBPacker.message_to_string(data)
			
		func to_bytes() -> PoolByteArray:
			return PBPacker.pack_message(data)
			
		func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
			var cur_limit = bytes.size()
			if limit != -1:
				cur_limit = limit
			var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
			if result == cur_limit:
				if PBPacker.check_required(data):
					if limit == -1:
						return PB_ERR.NO_ERRORS
				else:
					return PB_ERR.REQUIRED_FIELDS
			elif limit == -1 && result > 0:
				return PB_ERR.PARSE_INCOMPLETE
			return result
		
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
class Message:
	func _init():
		var service
		
		_agent_data = PBField.new("agent_data", PB_DATA_TYPE.MESSAGE, PB_RULE.OPTIONAL, 1, true, DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE])
		service = PBServiceField.new()
		service.field = _agent_data
		service.func_ref = funcref(self, "new_agent_data")
		data[_agent_data.tag] = service
		
		_world_data = PBField.new("world_data", PB_DATA_TYPE.MESSAGE, PB_RULE.OPTIONAL, 2, true, DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE])
		service = PBServiceField.new()
		service.field = _world_data
		service.func_ref = funcref(self, "new_world_data")
		data[_world_data.tag] = service
		
	var data = {}
	
	var _agent_data: PBField
	func get_agent_data() -> AgentData:
		return _agent_data.value
	func clear_agent_data() -> void:
		data[1].state = PB_SERVICE_STATE.UNFILLED
		_agent_data.value = DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE]
	func new_agent_data() -> AgentData:
		_agent_data.value = AgentData.new()
		return _agent_data.value
	
	var _world_data: PBField
	func get_world_data() -> WorldData:
		return _world_data.value
	func clear_world_data() -> void:
		data[2].state = PB_SERVICE_STATE.UNFILLED
		_world_data.value = DEFAULT_VALUES_3[PB_DATA_TYPE.MESSAGE]
	func new_world_data() -> WorldData:
		_world_data.value = WorldData.new()
		return _world_data.value
	
	func to_string() -> String:
		return PBPacker.message_to_string(data)
		
	func to_bytes() -> PoolByteArray:
		return PBPacker.pack_message(data)
		
	func from_bytes(bytes : PoolByteArray, offset : int = 0, limit : int = -1) -> int:
		var cur_limit = bytes.size()
		if limit != -1:
			cur_limit = limit
		var result = PBPacker.unpack_message(data, bytes, offset, cur_limit)
		if result == cur_limit:
			if PBPacker.check_required(data):
				if limit == -1:
					return PB_ERR.NO_ERRORS
			else:
				return PB_ERR.REQUIRED_FIELDS
		elif limit == -1 && result > 0:
			return PB_ERR.PARSE_INCOMPLETE
		return result
	
################ USER DATA END #################
