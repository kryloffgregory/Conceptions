import os
import struct
import mmap

block_size = 4
pack_format = '>I'
ANS = 0
PTR = 1
STP = 2
commands = {

	"JMP": (0x1, 1),
	"CJMP": (0x2, 2),
	"CLE": (0x3, 2),
	"ADD": (0x11, 2),
	"SUB": (0x12, 2),
	"MUL": (0x13, 2),
	"DIV": (0x14, 2),
	"INC": (0x15, 1),
	"DEC": (0x16, 1),
	"PUSH": (0x21, 1),
	"POP": (0x22, 1),
	"MOV":(0x23, 2),
	"RET": (0xfe, 0),
	"EXIT": (0xff, 0),
	"OUT": (0x31, 1),
	"OUTC": (0x32, 1),
	"INP": (0x33,1),
	"NXT": (0x41,0),
	"PRV": (0x42, 0)
}
commands_by_number = {}
def get_commands_by_number():
	for cmd in commands.items():
		commands_by_number[cmd[1][0]] = cmd[0]

def get_cell_value(memory, cell_num):
	return struct.unpack(pack_format, memory[cell_num * block_size : (cell_num + 1) * block_size])[0]

def update_cell_value(memory, cell_num, cell_value):
	memory[cell_num * block_size : (cell_num + 1) * block_size] = bytearray(struct.pack(pack_format, cell_value))

def NXT(memory, param1, flag, param2):
	update_cell_value(memory, PTR, get_cell_value(memory, PTR) + 4)
	return True

def PRV(memory, param1, flag, param2):
	update_cell_value(memory, PTR, get_cell_value(memory, PTR) - 4)
	return True

def ADD(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, param1, value1 + value2)
	NXT(memory, param1, flag, param2)
	return True

def SUB(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, param1, value1 - value2)
	NXT(memory, param1, flag, param2)
	return True

def MUL(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, param1, value1 * value2)
	NXT(memory, param1, flag, param2)
	return True

def DIV(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, param1, value1 // value2)
	NXT(memory, param1, flag, param2)
	return True

def OUT(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	print(value1)
	NXT(memory, param1, flag, param2)
	return True

def OUTC(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	print(chr(value1), end = '')
	NXT(memory, param1, flag, param2)
	return True

def INP(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	num = int(input())
	update_cell_value(memory, param1, num)
	NXT(memory, param1, flag, param2)
	return True

def JMP(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, PTR, param1)
	return True

def CJMP(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	if(value1 != 0):
		update_cell_value(memory, PTR, param2)
	else:
		NXT(memory, param1, flag, param2)
	return True

def RET(memory, param1, flag, param2):
	stp_val = get_cell_value(memory, STP)
	val = get_cell_value(memory, stp_val)
	update_cell_value(memory, PTR, val)
	POP(memory, 0, 0, 0)
	PRV(memory, 0, 0, 0)
	return True

def EXIT(memory, param1, flag, param2):
	return False

def INC(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, param1, value1 + 1)
	NXT(memory, param1, flag, param2)
	return True

def DEC(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, param1, value1 - 1)
	NXT(memory, param1, flag, param2)
	return True

def MOV(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, param1, value2)
	NXT(memory, param1, flag, param2)
	return True

def PUSH(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, STP, get_cell_value(memory, STP) + 1)
	update_cell_value(memory, get_cell_value(memory, STP), param1)
	NXT(memory, param1, flag, param2)
	return True

def POP(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	update_cell_value(memory, STP, get_cell_value(memory, STP) - 1)
	NXT(memory, param1, flag, param2)
	return True

def CLE(memory, param1, flag, param2):
	value1 = get_cell_value(memory, param1)
	value2 = get_cell_value(memory, param2)
	if(value1 <= value2):
		update_cell_value(memory, param1, 1)
	else:
		update_cell_value(memory, param1, 0)
	NXT(memory, param1, flag, param2)
	return True

def exec_command(memory):
	ptr = get_cell_value(memory, PTR)
	cmd_num = get_cell_value(memory, ptr)
	cmd_str = commands_by_number[cmd_num]
	return globals()[cmd_str](memory, get_cell_value(memory, ptr + 1), get_cell_value(memory, ptr + 2), get_cell_value(memory, ptr + 3))

def print_memory(memory):
	for i in range(40):
		print(get_cell_value(memory, i), end = ' ')
	print()

def exec(file):
	get_commands_by_number()
	file_size = os.path.getsize(file)
	file_on_disk = os.open(file, os.O_RDWR)
	memory = mmap.mmap(file_on_disk, file_size)

	while(exec_command(memory)):
		#print_memory(memory)
		pass
exec('code.dat')