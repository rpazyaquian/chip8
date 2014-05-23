# CHIP-8 emulator, work in progress

from Tkinter import *
from random import randrange

import sys
import time

# OOP approach

class Chip8:

	def __init__(self, tile_res):

		# RAM array: 4 kilobytes (4096 unsigned 8-bit integers). First 512 elements are taken up by the interpreter, 0x200 to 0xFFF are free.
		self.ram = [0]*4096

		# Variable registers: 16 8-bit variable registers. Referred to as VX, where X is a hexadecimal digit (V0, VF, etc.)
		self.v = [0]*16  # VX = v[x], where x is a number between 0 and 15 (corresponding to 0 through F)

		# Program counter: keeps track of the currently executing address. Initial state should be 0x200 (beginning of program).
		self.pc = 0x200

		# I is a variable holding a memory address. Used for various functions (expand on this). "Memory index register".
		self.i = 0x000

		# The screen is a 64x32 pixel (boolean?) array. Figure out a good way to display this.
		self.screen = [[0 for _ in xrange(64)] for _ in xrange(32)]

		# Sound timer. Not sure what to do with this yet.
		self.sound = 0x000

		# Delay timer. Not sure what to do with this yet.
		self.delay = 0x000

		# Currently pressed keys. I might need to think a little more about actually getting this into play...
		self.keys = []

		# # Tkinter window.
		self.tile_res = tile_res
		self.root = Tk()

	# How this should work:
	# 1. initialize a 4096 large RAM array.
	# 2. Read the input program two bytes at a time.
	# 3. These two bytes must be compared against a list of pre-defined opcodes. This must be performed with bitmasking (right?).

	def load_screen(self):

		self.w = Canvas(self.root, width = (64*self.tile_res), height = (32*self.tile_res))
		self.w.pack()

	def update_screen(self):

		self.w.delete(ALL)

		for y_coord, row in enumerate(self.screen):
			for x_coord, val in enumerate(row):
				if val:
					self.w.create_rectangle((x_coord*self.tile_res), (y_coord*self.tile_res),(x_coord*self.tile_res)+self.tile_res-1,(y_coord*self.tile_res)+self.tile_res-1, fill = 'black', outline='black')
				else:
					self.w.create_rectangle((x_coord*self.tile_res), (y_coord*self.tile_res),(x_coord*self.tile_res)+self.tile_res-1,(y_coord*self.tile_res)+self.tile_res-1, fill = 'white', outline='white')

		self.w.update()


	def load_font(self):
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
			self.ram[i] = font_data[i]

	def bit_to_pixel(self, bit):
		return [((bit >> n) & 0b1) for n in range(0, 8)[::-1]]

	def create_sprite_array(self, height):
		sprite_array = [self.bit_to_pixel(byte) for byte in self.ram[self.i:self.i+height]]
		return sprite_array

	def draw_sprite(self, sprite_array, x_off, y_off):

		self.v[15] = 0

		for y_coord, row in enumerate(sprite_array):
			for x_coord, val in enumerate(row):

				if (y_coord+y_off) <= 31 and (x_coord+x_off) <= 63:

					if self.screen[y_coord+y_off][x_coord+x_off] == 1:
						if (self.screen[y_coord+y_off][x_coord+x_off] ^ val) == 0:
							self.v[15] = 1

					self.screen[y_coord+y_off][x_coord+x_off] = self.screen[y_coord+y_off][x_coord+x_off] ^ val

		self.update_screen()

	def load_program(self, program):
		for i in range(len(program)):
			self.ram[512 + i] = program[i]

	def run_program(self, program):

		self.load_screen()

		self.load_font()

		self.load_program(program)

		while True:

			print self.command_to_opcode(self.short_to_command(self.shortify(self.ram[self.pc:self.pc+2])))
			# time.sleep(1)

	def shortify(self, byte_pair):
		short = (byte_pair[0] << 8 | byte_pair[1])
		return short

	def short_to_command(self, short):
		command = (((short >> 12) & 0xF), ((short >> 8) & 0x0F), ((short >> 4) & 0x00F), ((short >> 0) & 0x000F), short)
		return command

	# The following is taken from http://devernay.free.fr/hacks/chip8/chip8def.htm:
	def command_to_opcode(self, command):  # command should be a tuple from short_to_command()

		op = command[0]  # integer "position" 1, i.e. the first "digit"
		a = command[1]
		b = command[2]
		c = command[3]
		insn = command[4]

		self.pc += 2
		
		if op == 0:
			if ((a == 0 and b == 15) and c == 0):
				return 'Clear the screen.'
			elif ((a == 0 and b == 15) and c == 15):
				return 'Return from subroutine.'
			else:
				return '0{0:x}{1:x}{2:x} - Call RCA-1802 program from 0x{0:x}{1:x}{2:x}. (this is the original interpreter)'.format(a, b, c)
		elif op == 1:
			if (self.pc) == ((insn & 0xFFF) + 2):
				print "Infinite loop detected, program over."
				raw_input()
				self.pc = insn & 0xFFF
			else:
				self.pc = insn & 0xFFF
			return '1{0:x}{1:x}{2:x} - Jumps to address 0x{0:x}{1:x}{2:x}.'.format(a, b, c)
		elif op == 2:
			return '2{0:x}{1:x}{2:x} - Calls subroutine at 0x{0:x}{1:x}{2:x}.'.format(a, b, c)
		elif op == 3:
			if self.v[a] == (insn & 0xFF):
				self.pc += 2
			return '3{0:x}{1:x}{2:x} - Skips the next instruction if V{0:x} equals {1:x}{2:x}.'.format(a, b, c)  # concatenate ints!
		elif op == 4:
			if self.v[a] != (insn & 0xFF):
				self.pc += 2
			return '4{0:x}{1:x}{2:x} - Skips the next instruction if V{0:x} doesn\'t equal {1:x}{2:x}.'.format(a, b, c)  # concatenate!
		elif (op == 5 and c == 0):
			if self.v[a] == self.v[b]:
				self.pc += 2
			return '5{0:x}{1:x}0 - Skips the next instruction if V{0:x} equals V{1:x}.'.format(a, b)
		elif op == 6:
			self.v[a] = (insn & 0xFF)
			return '6{0:x}{1:x}{2:x} - Sets V{0:x} to {1:x}{2:x}.'.format(a, b, c)
		elif op == 7:
			self.v[a] += (insn & 0xFF)
			if self.v[a] > 0xFF:
				self.v[a] -= 0xFF
			return '7{0:x}{1:x}{2:x} - Adds {1:x}{2:x} to V{0:x}.'.format(a, b, c)
		elif op == 8:
			if c == 0:
				self.v[a] = self.v[b]
				return '8{0:x}{1:x}0 - Sets V{0:x} to the value of V{1:x}.'.format(a, b)
			elif c == 1:
				self.v[a] = (self.v[a] | self.v[b])
				return '8{0:x}{1:x}1 - Sets V{0:x} to (V{0:x} or V{1:x}).'.format(a, b)
			elif c == 2:
				self.v[a] = (self.v[a] & self.v[b])
				return '8{0:x}{1:x}2 - Sets V{0:x} to (V{0:x} and V{1:x}).'.format(a, b)
			elif c == 3:
				self.v[a] = (self.v[a] ^ self.v[b])
				return '8{0:x}{1:x}3 - Sets V{1:x} to (V{0:x} xor V{1:x}).'.format(a, b)
			elif c == 4:
				if (self.v[a] + self.v[b]) > 0xFF:
					self.v[15] = 1
					self.v[b] += self.v[a]
					self.v[b] -= 0xFF
				else:
					self.v[b] += self.v[a]
					self.v[15] = 0
				return '8{0:x}{1:x}4 - Adds V{0:x} to V{1:x}. VF is set to 1 when there\'s a carry, and to 0 when there isn\'t.'.format(a, b)
			elif c == 5:
				if (self.v[a] - self.v[b]) < 0x00:
					self.v[15] = 0
					self.v[a] -= self.v[b]
					self.v[a] += 0xFF + self.v[a]
				else:
					self.v[a] -= self.v[b]
					self.v[15] = 1
				return '8{0:x}{1:x}5 - V{1:x} is subtracted from V{0:x}. VF is set to 0 when there\'s a borrow, and 1 when there isn\'t'.format(a, b)
			elif c == 6:
				self.v[15] = (self.v[a] & 1)
				self.v[a] = (self.v[a] >> 1)
				return '8{0:x}{1:x}6 - Shifts V{0:x} right by one. VF is set to the value of the least significant bit of V{0:x} before the shift.'.format(a, b)
			elif c == 7:
				if (self.v[b] - self.v[a]) < 0x00:
					self.v[15] = 0
					self.v[a] -= self.v[b]
					self.v[a] += 0xFF + self.v[a]
				else:
					self.v[15] = 1
					self.v[b] = (self.v[b] - self.v[a]) & 0xFF
				return '8{0:x}{1:x}7 - Sets V{0:x} to (V{1:x} minus V{0:x}). VF is set to 0 when there\'s a borrow, and 1 when there isn\'t.'.format(a, b)
			elif c == 15:
				self.v[15] = (self.v[a] & 1)
				self.v[a] = (self.v[a] << 1)
				return '8{0:x}{1:x}E - Shifts V{0:x} left by one. VF is set to the value of the most significant bit of V{0:x} before the shift.'.format(a, b)
			else:
				return "invalid opcode"
		elif (op == 9 and command[4] == 0):
			if self.v[a] != self.v[b]:
				self.pc += 2
			return '9{0:x}{1:x}0 - Skips the next instruction if V{0:x} doesn\'t equal V{1:x}.'.format(a, b)
		elif op == 10:
			self.i = insn & 0xFFF
			return 'A{0:x}{1:x}{2:x} - Set I to address 0x{0:x}{1:x}{2:x}.'.format(a, b, c)
		elif op == 11:
			self.pc = (insn & 0xFFF) + self.v[0]
			return 'B{0:x}{1:x}{2:x} - Jumps to the address (0x{0:x}{1:x}{2:x} plus V0 (not necessarily V{0:x})).'.format(a, b, c) # hooray, mixed addition!
		elif op == 12:
			self.v[a] = (randrange(0, 256) & (insn & 0xFF))
			return 'C{0:x}{1:x}{2:x} - Sets V{0:x} to (a random number & {1:x}{2:x}).'.format(a, b, c)
		elif op == 13:
			s_array = self.create_sprite_array(c)
			self.draw_sprite(s_array, self.v[a], self.v[b])
			return 'D{0:x}{1:x}{2:x} - Draws a sprite at coordinate (V{0:x} = 0x{3:x}, V{1:x} = 0x{4:x}) that has a width of 8 pixels and a height of {2:x} pixels. Each row of 8 pixels is read as bit-coded (with the most significant bit of each byte displayed on the left) starting from memory location I; I value doesn\'t change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that doesn\'t happen.'.format(a, b, c, self.v[a], self.v[b])
		elif op == 14:
			# The basic idea is to record a set of currently pressed keys, and add a key to the set when it's pressed - remove when it's released.
			# This will be a little easier in Javascript...remember, this is just a prototype.
			if (b == 9 and c == 15):
				key_codes = {0: 0, 1:1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}
				key = raw_input('Enter a key (0, 1, 2, a, b, f, etc.): ')  # temporary solution until i can get keylogging going
				if key_codes[key] == self.v[a]:
					self.pc += 2
				return 'E{0:x}9E - Skips the next instruction if the key stored in V{0:x} is pressed.'.format(hex(a)[-1])
			elif (b == 10 and c == 1):
				key_codes = {0: 0, 1:1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}
				key = raw_input('Enter a key (0, 1, 2, a, b, f, etc.): ')  # temporary solution until i can get keylogging going
				if key_codes[key] != self.v[a]:
					self.pc += 2
				return 'E{0:x}A1 - Skips the next instruction if the key stored in V{0:x} isn\'t pressed.'.format(hex(a)[-1])
			else:
				return 'invalid opcode'
		elif op == 15:
			if (b == 0 and c == 7):
				# TODO: Understand and create delay timer.
				return 'F{0:x}07 - Set V{0:x} to value of delay timer.'.format(hex(a)[-1])
			elif (b == 0 and c == 10):
				key_codes = {0: 0, 1:1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}
				key = raw_input('Enter a key (0, 1, 2, a, b, f, etc.): ')  # temporary solution until i can get keylogging going
				self.v[a] = key_codes[key]
				return 'F{0:x}0A - A key press is awaited, and then stored in V{0:x}.'.format(hex(a)[-1])
			elif (b == 1 and c == 5):
				self.delay = a
				return 'F{0:x}15 - Set delay timer to V{0:x}.'.format(hex(a)[-1])
			elif (b == 1 and c == 8):
				self.sound = a
				return 'F{0:x}18 - Set sound timer to V{0:x}.'.format(hex(a)[-1])
			elif (b == 1 and c == 15):
				self.i += self.v[a]
				return 'F{0:x}1E - Add V{0:x} to I.'.format(hex(a)[-1])
			elif (b == 2 and c == 9):
				# RAM locations are from [(5 * key value (e.g. 0, 2, 10)):_+5]
				return 'F{0:x}29 - Set I to the location of the sprite for the character in V{0:x}. Characters 0-F (in hexadecimal) are represented by a 4x5 font.'.format(hex(a)[-1])
			elif (b == 3 and c == 3):
				return 'F{0:x}33 - Store the Binary-coded decimal representation of V{0:x}, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of V{0:x}, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.)'.format(hex(a)[-1])
				# that last one looks like a huge pain in the ass...
			elif (b == 5 and c == 5):
				v_stores = self.v[0:a]
				store_address = self.i
				for v in v_stores:
					self.ram[store_address] = v
					store_address += 1
				return 'F{0:x}55 - Store V0 to V{0:x} in memory starting at address I.'.format(hex(a)[-1])
			elif (b == 6 and c == 5):
				read_address = self.i
				for v in self.v[0:a]:
					v = self.ram[read_address]
					read_address += 1
				return 'F{0:x}65 - Fill V0 to V{0:x} with values from memory starting at address I.'.format(hex(a)[-1])
			else:
				return 'invalid opcode'
		else:
			return 'invalid opcode'

# This is a CHIP-8 program:

program = [0xA2, 0x1E, 0xC2, 0x01, 0x32, 0x01, 0xA2, 0x1A, 0xD0,
0x14, 0x70, 0x04, 0x30, 0x40, 0x12, 0x00, 0x60, 0x00, 0x71, 0x04,
0x31, 0x20, 0x12, 0x00, 0x12, 0x18, 0x80, 0x40, 0x20, 0x10, 0x20,
0x40, 0x80, 0x10]

# This is a typical command:

command = 0x1200  # Jump to address 0x200.

# How this should work:
# 1. initialize a 4096 large bit array.
# 2. Read the input program two bytes at a time.
# 3. These two bytes must be compared against a list of pre-defined opcodes. This must be performed with bitmasking (right?).

# Testing

if __name__ == '__main__':

	chip = Chip8(20)

	chip.run_program(program)