import json
import struct
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
	"RET": (0xff, 0),
	"OUT": (0x31, 1),
	"OUTC": (0x32, 1),
	"INP": (0x33,1),
	"NXT": (0x41,0)
}
# 0 - reg for ans
# 1 - reg for pointer
# 2 - reg for stacktop
def compile_func(lines):
	res = []
	vars = {}
	cur_cell = 0
	for num_line, line in enumerate(lines):
		if(line.find('=') != -1):
			varname, varvalue = line.split('=')
			varname.strip()
			varvalue.strip()
			vars[varname] = cur_cell
			res.append(int(varvalue))
			cur_cell += 1
		else:
			tokens = line.strip().split(' ')
			tokens = [token.strip() for token in tokens if len(token.strip()) > 0]
			tokens = [vars[token] + 3 if token in vars else token for token in tokens ]
			print(tokens)
			cmd = tokens[0]
			if(cmd not in commands):
				print("Unknown command: " + cmd)
				return False
			else:
				code, args_num = commands[cmd]
				if(len(tokens) != args_num + 1):
					print("Wrong number of arguments of command: " + cmd)
					return False
				res.append(code)
				args = tokens[1:]
				if(args_num > 0):
					res.append(int(args[0]))
				else:
					res.append(0)
				res.append(0)
				if(args_num == 2):
					res.append(int(args[1]))
				else:
					res.append(0)
	res = [0, len(vars) + 3, 0] + res
	res[2] = len(res)
	res.append(0)
	return res
	
def serialize(code_array, file):
	code_file = open(file, 'wb+')
	for cell in code_array:
		code_file.write(bytearray(struct.pack(">I", cell)))

fi = open("program.txt", "r")
program = fi.readlines()
res = compile_func(program)
print(res)
serialize(res, 'code.dat')


