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
	"RET": (0xfe, 0),
	"EXIT": (0xff, 0),
	"OUT": (0x31, 1),
	"OUTC": (0x32, 1),
	"INP": (0x33,1),
	"NXT": (0x41,0),
	"PRV": (0x42, 0)
}
# 0 - reg for ans (unused)
# 1 - reg for pointer
# 2 - reg for stacktop
def compile_func(func_name, lines, code_array, global_vars, func_entries):
	res = code_array
	start_cell = len(code_array)
	vars = {}
	labels = {}
	cur_cell = start_cell
	for num_line, line in enumerate(lines):
		line.strip()
		if(line[0] == '@'):
			label_name = line[1:].strip()
			labels[label_name] = len(res)
			continue
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
			tokens = [vars[token] if token in vars else token for token in tokens ]
			tokens = [global_vars[token] if token in global_vars else token for token in tokens ]
			
			cmd = tokens[0]

			if(cmd in func_entries):
				res += [0x21, len(res) + 8, 0, 0]
				res += [0x1, func_entries[cmd], 0, 0]
				continue
			if(cmd == func_name):
				res +=[0x21, len(res)+ 8, 0, 0]
				res +=[0x1, start_cell + len(vars), 0, 0]
			if(cmd == "GOTO"):
				if(len(tokens) != 2):
					print("Wrong number of arguments of command: " + cmd)
					return False
				dest = tokens[1]
				if(dest not in labels):
					print("Unknown label: " + dest)
					return False
				res += [0x1, labels[dest], 0, 0]
				continue
			if(cmd == "IF"):
				if(len(tokens) != 3):
					print("Wrong number of arguments of command: " + cmd)
					return False
				if(tokens[2] in func_entries):
					res += [0x21, len(res)+ 8, 0, 0]
					res += [0x2, tokens[1], 0, func_entries[tokens[2]]]
				elif(tokens[2] == func_name):
					res += [0x21, len(res)+ 12, 0, 0]
					res += [0x2, tokens[1], 0, start_cell + len(vars)]
					res += [0x22, 0, 0, 0]
				else:
					print("Unknown function " + tokens[2])
					return False
				continue
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
	return start_cell + len(vars), res


def compile_program(program, recursion_limit=1000):
	program.append('END:')
	now_globals = True
	global_vars = {}
	code = [0, 0, 0]
	cur_func_lines = []
	cur_func_name = ""
	func_entries = {}
	for line in program:
		line.strip()
		if(now_globals):
			if(line.find('=') != -1):
				varname, varvalue = line.split('=')
				varname.strip()
				varvalue.strip()

				global_vars[varname] = len(code)
				code.append(int(varvalue))
			else:
				now_globals = False
		
		if(now_globals == False):
			if(line.find(':') != -1):
				if(len(cur_func_lines) != 0):
					entry_point, code = compile_func(cur_func_name, cur_func_lines, code, global_vars, func_entries)
					func_entries[cur_func_name] = entry_point
					if(cur_func_name == 'MAIN'):
						code[1] = entry_point
				cur_func_lines = []
				cur_func_name = line.strip()[:-1]
			else:
				cur_func_lines.append(line)
	code += [0xff, 0, 0, 0]
	code += [len(code) - 4]
	code[2] = len(code) - 1
	code += [0] * recursion_limit
	return code

def serialize(code_array, file):
	code_file = open(file, 'wb+')
	for cell in code_array:
		code_file.write(bytearray(struct.pack(">I", cell)))

fi = open("program.txt", "r")
program = fi.readlines()
res = compile_program(program)
print(res)
serialize(res, 'code.dat')


