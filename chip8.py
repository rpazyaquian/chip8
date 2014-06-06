# CHIP-8 emulator, work in progress
from random import randrange

import pyglet as pyg

import sys
import time


# Window properties

window = pyg.window.Window()

margin = 10

height = 320
width = 640

window.height = height + (margin*2)
window.width = width + (margin*2)


# Game properties

# RAM array: 4 kilobytes (4096 unsigned 8-bit integers). First 512 elements are taken up by the interpreter, 0x200 to 0xFFF are free.
ram = [0]*4096

# Variable registers: 16 8-bit variable registers. Referred to as VX, where X is a hexadecimal digit (V0, VF, etc.)
v = [0]*16  # VX = v[x], where x is a number between 0 and 15 (corresponding to 0 through F)

# Program counter: keeps track of the currently executing address. Initial state should be 0x200 (beginning of program).
# so, for example, at the end of an opcode, pc will change.
# on update, i run a function run_opcode().
# this function runs the opcode at the current value of pc.
# i will need a program byte array.
# the function itself will change pc and everything.
pc = 0x200

# I is a variable holding a memory address. Used for various functions (expand on this). "Memory index register".
i = 0x000

# The screen is a 64x32 pixel (boolean?) array. Figure out a good way to display this.
screen = [[0 for _ in xrange(64)] for _ in xrange(32)]

# Sound timer. Not sure what to do with this yet.
sound = 0x03c

# Delay timer. Not sure what to do with this yet.
delay = 0x03c

# Currently pressed keys.
keys = []

# Translation from pyglet inputs to key values.
keycodes = {48: 0, 49: 1, 50: 2, 51: 3, 52: 4, 53: 5, 54: 6, 55: 7, 56: 8, 57: 9, 97: 10, 98: 11, 99: 12, 100: 13, 101: 15, 102: 15}

# Subroutine stack. An array of 16 shorts (32 bytes) that will hold a bunch of addresses, I assume.
# Also the stack pointer, which points to the current position of the stack.
stack = [0]*16
sp = 0x000


# Graphics functions

def update_screen():
	# DRAW the entire screen.
	# updating the screen ARRAY is done within opcode functions.

	for y_coord, row in enumerate(screen):
		for x_coord, val in enumerate(row):
			if val:
				draw_square((x_coord*10, y_coord*10), ((x_coord*10)+10, (y_coord*10)+10))

def draw_square(tl, br):

	global window

	# begins drawing from the lower left. remember this.
	pyg.graphics.draw(3, pyg.gl.GL_TRIANGLES, ('v2i', (tl[0]+margin, window.height-tl[1]-margin, tl[0]+margin, window.height-br[1]-margin, br[0]+margin, window.height-br[1]-margin)))  # (0,0), (0, 10), (10, 10)
	pyg.graphics.draw(3, pyg.gl.GL_TRIANGLES, ('v2i', (br[0]+margin, window.height-br[1]-margin, br[0]+margin, window.height-tl[1]-margin, tl[0]+margin, window.height-tl[1]-margin)))  # (10, 10), (10, 0), (0, 10)

@window.event
def on_draw():
	window.clear()
	update_screen()

@window.event
def on_key_press(symbol, modifiers):
	if symbol in keycodes:
		keys.append(keycodes[symbol])

@window.event
def on_key_release(symbol, modifiers):
	if symbol in keycodes:
		keys.remove(keycodes[symbol])


# Logic and game functions

# this is the function where all the game updating logic happens!
# here, you will define what happens in each frame.
# so, you would say:
# "for each frame, run 10 opcodes, redraw the screen, tick the delay timer, and tick the sound timer"
def update(dt):
	for i in range(0, 10):
		run_opcode()
	tick_delay()
	tick_sound()

def run_opcode():
	# something like...
	command_to_opcode(short_to_command(shortify(ram[pc:pc+2])))
	# where the program is loaded into RAM at the beginning of main program run.

def load_program(program):
	for i in range(len(program)):
		ram[512 + i] = program[i]

def load_font():
	font_data = [
	0xF0, 0x90, 0x90, 0x90, 0xF0,
	0x20, 0x60, 0x20, 0x20, 0x70,
	0xF0, 0x10, 0xF0, 0x80, 0xF0,
	0xF0, 0x10, 0xF0, 0x10, 0xF0,
	0x90, 0x90, 0xF0, 0x10, 0x10,
	0xF0, 0x80, 0xF0, 0x10, 0xF0,
	0xF0, 0x80, 0xF0, 0x90, 0xF0,
	0xF0, 0x10, 0x20, 0x40, 0x40,
	0xF0, 0x90, 0xF0, 0x90, 0xF0,
	0xF0, 0x90, 0xF0, 0x10, 0xF0,
	0xF0, 0x90, 0xF0, 0x90, 0x90,
	0xE0, 0x90, 0xE0, 0x90, 0xE0,
	0xF0, 0x80, 0x80, 0x80, 0xF0,
	0xE0, 0x90, 0x90, 0x90, 0xE0,
	0xF0, 0x80, 0xF0, 0x80, 0xF0,
	0xF0, 0x80, 0xF0, 0x80, 0x80
	]

	for i in range(len(font_data)):
		ram[i] = font_data[i]

def tick_delay():
	global delay
	if delay > 0:
		delay -= 1

def tick_sound():
	global sound
	if sound > 0:
		sound -= 1

def draw_sprite(sprite_array, x_off, y_off):

	global v
	global screen

	v[15] = 0

	for y_coord, row in enumerate(sprite_array):
		for x_coord, val in enumerate(row):

			if (y_coord+y_off) <= 31 and (x_coord+x_off) <= 63:

				if screen[y_coord+y_off][x_coord+x_off] == 1:
					if (screen[y_coord+y_off][x_coord+x_off] ^ val) == 0:
						v[15] = 1

				screen[y_coord+y_off][x_coord+x_off] = screen[y_coord+y_off][x_coord+x_off] ^ val

def bit_to_pixel(bit):
	return [((bit >> n) & 0b1) for n in range(0, 8)[::-1]]

def create_sprite_array(height):
	sprite_array = [bit_to_pixel(byte) for byte in ram[i:i+height]]
	return sprite_array

def shortify(byte_pair):
	short = (byte_pair[0] << 8 | byte_pair[1])
	return short

def short_to_command(short):
	command = (((short >> 12) & 0xF), ((short >> 8) & 0x0F), ((short >> 4) & 0x00F), ((short >> 0) & 0x000F), short)
	return command

# this function isn't working yet. ignore it ---v
def command_to_opcode(command):  # command should be a tuple from short_to_command()

	global ram
	global v
	global i
	global pc
	global screen
	global sound
	global delay
	global keys
	global keycodes
	global stack
	global sp

	op = command[0]  # integer "position" 1, i.e. the first "digit"
	a = command[1]
	b = command[2]
	c = command[3]
	insn = command[4]

	pc += 2
	
	if op == 0:
		if ((a == 0 and b == 14) and c == 0):
			# clear_screen():
				# set screen to all 0's
			return 'Clear the screen.'
		elif ((a == 0 and b == 14) and c == 14):
			# return_subroutine():
				# 
			sp -= 1
			pc = stack[sp]
			return 'Return from subroutine.'
		else:
			return '0{0:x}{1:x}{2:x} - Call RCA-1802 program from 0x{0:x}{1:x}{2:x}. (this is the original interpreter)'.format(a, b, c)
	elif op == 1:
		if (pc) == ((insn & 0xFFF) + 2):
			break
			# print "Infinite loop detected, program over."
			# raw_input()
			pc = insn & 0xFFF
		else:
			pc = insn & 0xFFF
		return '1{0:x}{1:x}{2:x} - Jumps to address 0x{0:x}{1:x}{2:x}.'.format(a, b, c)
	elif op == 2:
		stack[sp] = pc
		sp += 1
		pc = insn & 0xFFF
		# print stack
		return '2{0:x}{1:x}{2:x} - Calls subroutine at 0x{0:x}{1:x}{2:x}.'.format(a, b, c)
	elif op == 3:
		if v[a] == (insn & 0xFF):
			pc += 2
		return '3{0:x}{1:x}{2:x} - Skips the next instruction if V{0:x} equals {1:x}{2:x}.'.format(a, b, c)  # concatenate ints!
	elif op == 4:
		if v[a] != (insn & 0xFF):
			pc += 2
		return '4{0:x}{1:x}{2:x} - Skips the next instruction if V{0:x} doesn\'t equal {1:x}{2:x}.'.format(a, b, c)  # concatenate!
	elif (op == 5 and c == 0):
		if v[a] == v[b]:
			pc += 2
		return '5{0:x}{1:x}0 - Skips the next instruction if V{0:x} equals V{1:x}.'.format(a, b)
	elif op == 6:
		v[a] = (insn & 0xFF)
		return '6{0:x}{1:x}{2:x} - Sets V{0:x} to {1:x}{2:x}.'.format(a, b, c)
	elif op == 7:
		v[a] += (insn & 0xFF)
		if v[a] > 0xFF:
			v[a] -= 0xFF
		return '7{0:x}{1:x}{2:x} - Adds {1:x}{2:x} to V{0:x}.'.format(a, b, c)
	elif op == 8:
		if c == 0:
			v[a] = v[b]
			return '8{0:x}{1:x}0 - Sets V{0:x} to the value of V{1:x}.'.format(a, b)
		elif c == 1:
			v[a] = (v[a] | v[b])
			return '8{0:x}{1:x}1 - Sets V{0:x} to (V{0:x} or V{1:x}).'.format(a, b)
		elif c == 2:
			v[a] = (v[a] & v[b])
			return '8{0:x}{1:x}2 - Sets V{0:x} to (V{0:x} and V{1:x}).'.format(a, b)
		elif c == 3:
			v[a] = (v[a] ^ v[b])
			return '8{0:x}{1:x}3 - Sets V{1:x} to (V{0:x} xor V{1:x}).'.format(a, b)
		elif c == 4:
			if (v[a] + v[b]) > 0xFF:
				v[15] = 1
				v[b] += v[a]
				v[b] -= 0xFF
			else:
				v[b] += v[a]
				v[15] = 0
			return '8{0:x}{1:x}4 - Adds V{0:x} to V{1:x}. VF is set to 1 when there\'s a carry, and to 0 when there isn\'t.'.format(a, b)
		elif c == 5:
			if (v[a] - v[b]) < 0x00:
				v[15] = 0
				v[a] -= v[b]
				v[a] += 0xFF + v[a]
			else:
				v[a] -= v[b]
				v[15] = 1
			return '8{0:x}{1:x}5 - V{1:x} is subtracted from V{0:x}. VF is set to 0 when there\'s a borrow, and 1 when there isn\'t'.format(a, b)
		elif c == 6:
			v[15] = (v[a] & 1)
			v[a] = (v[a] >> 1)
			return '8{0:x}{1:x}6 - Shifts V{0:x} right by one. VF is set to the value of the least significant bit of V{0:x} before the shift.'.format(a, b)
		elif c == 7:
			if (v[b] - v[a]) < 0x00:
				v[15] = 0
				v[a] -= v[b]
				v[a] += 0xFF + v[a]
			else:
				v[15] = 1
				v[b] = (v[b] - v[a]) & 0xFF
			return '8{0:x}{1:x}7 - Sets V{0:x} to (V{1:x} minus V{0:x}). VF is set to 0 when there\'s a borrow, and 1 when there isn\'t.'.format(a, b)
		elif c == 14:
			v[15] = (v[a] & 1)
			v[a] = (v[a] << 1)
			return '8{0:x}{1:x}E - Shifts V{0:x} left by one. VF is set to the value of the most significant bit of V{0:x} before the shift.'.format(a, b)
		else:
			return "invalid opcode"
	elif (op == 9 and command[4] == 0):
		if v[a] != v[b]:
			pc += 2
		return '9{0:x}{1:x}0 - Skips the next instruction if V{0:x} doesn\'t equal V{1:x}.'.format(a, b)
	elif op == 10:
		i = insn & 0xFFF
		return 'A{0:x}{1:x}{2:x} - Set I to address 0x{0:x}{1:x}{2:x}.'.format(a, b, c)
	elif op == 11:
		pc = (insn & 0xFFF) + v[0]
		return 'B{0:x}{1:x}{2:x} - Jumps to the address (0x{0:x}{1:x}{2:x} plus V0 (not necessarily V{0:x})).'.format(a, b, c) # hooray, mixed addition!
	elif op == 12:
		v[a] = (randrange(0, 256) & (insn & 0xFF))
		return 'C{0:x}{1:x}{2:x} - Sets V{0:x} to (a random number & {1:x}{2:x}).'.format(a, b, c)
	elif op == 13:
		s_array = create_sprite_array(c)
		# print v
		draw_sprite(s_array, v[a], v[b])
		return 'D{0:x}{1:x}{2:x} - Draws a sprite at coordinate (V{0:x} = 0x{3:x}, V{1:x} = 0x{4:x}) that has a width of 8 pixels and a height of {2:x} pixels. Each row of 8 pixels is read as bit-coded (with the most significant bit of each byte displayed on the left) starting from memory location I; I value doesn\'t change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that doesn\'t happen.'.format(a, b, c, v[a], v[b])
	elif op == 14:
		# The basic idea is to record a set of currently pressed keys, and add a key to the set when it's pressed - remove when it's released.
		# This will be a little easier in Javascript...remember, this is just a prototype.
		if (b == 9 and c == 14):
			if v[a] in keys:
				pc += 2
			return 'E{0:x}9E - Skips the next instruction if the key stored in V{0:x} is pressed.'.format(a)
		elif (b == 10 and c == 1):
			if v[a] not in keys: 
				pc += 2
			return 'E{0:x}A1 - Skips the next instruction if the key stored in V{0:x} isn\'t pressed.'.format(a)
		else:
			return 'invalid opcode'
	elif op == 15:
		if (b == 0 and c == 7):
			v[a] = delay
			return 'F{0:x}07 - Set V{0:x} to value of delay timer.'.format(a)
		elif (b == 0 and c == 10):
			key_codes = {0: 0, 1:1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}
			key = raw_input('Enter a key (0, 1, 2, a, b, f, etc.): ')  # temporary solution until i can get keylogging going
			v[a] = key_codes[key]
			return 'F{0:x}0A - A key press is awaited, and then stored in V{0:x}.'.format(a)
		elif (b == 1 and c == 5):
			delay = a
			return 'F{0:x}15 - Set delay timer to V{0:x}.'.format(a)
		elif (b == 1 and c == 8):
			sound = a
			return 'F{0:x}18 - Set sound timer to V{0:x}.'.format(a)
		elif (b == 1 and c == 14):
			i += v[a]
			return 'F{0:x}1E - Add V{0:x} to I.'.format(a)
		elif (b == 2 and c == 9):
			# RAM locations are from [(5 * key value (e.g. 0, 2, 10)):_+5]
			# e.g. ram[v[a] * 5], with VX = 0, will drop you off at ram[0] and read from there to ram[4].
			# '0' font data is located from ram[0] to ram[4] (5 pixel height total).
			# '1' font data is located from ram[5] to ram[9] (5 pixel height total).
			# etc.
			i = (a * 5)
			return 'F{0:x}29 - Set I to the location of the sprite for the character in V{0:x}. Characters 0-F (in hexadecimal) are represented by a 4x5 font.'.format(a)
		elif (b == 3 and c == 3):
			ones = (v[a] / 1) % 10
			tens = (v[a] / 10) % 10
			hunds = (v[a] / 100) % 10

			ram[i] = hunds
			ram[i + 1] = tens
			ram[i + 2] = ones
			return 'F{0:x}33 - Store the Binary-coded decimal representation of V{0:x}, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of V{0:x}, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.)'.format(a)
		elif (b == 5 and c == 5):
			v_stores = v[0:a]
			store_address = i
			for v in v_stores:
				ram[store_address] = v
				store_address += 1
			return 'F{0:x}55 - Store V0 to V{0:x} in memory starting at address I.'.format(a)
		elif (b == 6 and c == 5):
			read_address = i
			for v_slot in v[0:a]:
				v_slot = ram[read_address]
				read_address += 1
			return 'F{0:x}65 - Fill V0 to V{0:x} with values from memory starting at address I.'.format(a)
		else:
			return 'invalid opcode'
	else:
		return 'invalid opcode'

# Main loop

if __name__ == '__main__':
	file = open(sys.argv[1], 'rb')
	program = bytearray(file.read())
	file.close()

	load_program(program)
	load_font()

	pyg.clock.schedule_interval(update, 1/60.0)

	pyg.app.run()  # goes absolutely last