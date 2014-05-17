# CHIP-8 emulator, work in progress

from random import randrange

# OOP approach

class Chip8:

	def __init__(self):

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

	# How this should work:
	# 1. initialize a 4096 large RAM array.
	# 2. Read the input program two bytes at a time.
	# 3. These two bytes must be compared against a list of pre-defined opcodes. This must be performed with bitmasking (right?).

	def bit_to_pixel(self, bit):
		return [((bit >> n) & 0b1) for n in range(0, 8)[::-1]]

	def create_sprite_array(self, height):
		sprite_array = [self.bit_to_pixel(byte) for byte in self.ram[self.i:self.i+height]]
		return sprite_array

	def draw_sprite(self, sprite_array, x_off, y_off):

		self.v[15] = 0

		for y_coord, row in enumerate(sprite_array):
			for x_coord, val in enumerate(row):

				if (y_coord+y_off) <= 63 and (x_coord+x_off) <= 31:

					if self.screen[y_coord+y_off][x_coord+x_off] == 1:
						if (self.screen[y_coord+y_off][x_coord+x_off] ^ val) == 0:
							self.v[15] = 1

					self.screen[y_coord+y_off][x_coord+x_off] = self.screen[y_coord+y_off][x_coord+x_off] ^ val

	def load_program(self, program):
		for i in range(len(program)):
			self.ram[512 + i] = program[i]

	def run_program(self, program):

		self.load_program(program)

		for i in range(len(program) * 10):

			print self.command_to_opcode(self.short_to_command(self.shortify(self.ram[self.pc:self.pc+2])))

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

		print self.pc

		self.pc += 2
		
		if op == 0:
			if ((a == 0 and b == 15) and c == 0):
				return 'Clear the screen.'
			elif ((a == 0 and b == 15) and c == 15):
				return 'Return from subroutine.'
			else:
				return '0{0}{1}{2} - Call RCA-1802 program from 0x{0}{1}{2}. (this is the original interpreter)'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 1:
			self.pc = insn & 0xFFF
			return '1{0}{1}{2} - Jumps to address 0x{0}{1}{2}.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 2:
			return '2{0}{1}{2} - Calls subroutine at 0x{0}{1}{2}.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 3:
			if self.v[a] == (insn & 0xFF):
				self.pc += 2
			return '3{0}{1}{2} - Skips the next instruction if V{0} equals {1}{2}.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])  # concatenate ints!
		elif op == 4:
			if self.v[a] != (insn & 0xFF):
				self.pc += 2
			return '4{0}{1}{2} - Skips the next instruction if V{0} doesn\'t equal {1}{2}.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])  # concatenate!
		elif (op == 5 and c == 0):
			if self.v[a] == self.v[b]:
				self.pc += 2
			return '5{0}{1}0 - Skips the next instruction if V{0} equals V{1}.'.format(hex(a)[-1], hex(b)[-1])
		elif op == 6:
			self.v[a] = (insn & 0xFF)
			return '6{0}{1}{2} - Sets V{0} to {1}{2}.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 7:
			self.v[a] += (insn & 0xFF)
			if self.v[a] > 0xFF:
				self.v[a] -= 0xFF
			return '7{0}{1}{2} - Adds {1}{2} to V{0}.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 8:
			if c == 0:
				self.v[a] = self.v[b]
				return '8{0}{1}0 - Sets V{0} to the value of V{1}.'.format(hex(a)[-1], hex(b)[-1])
			elif c == 1:
				self.v[a] = (self.v[a] | self.v[b])
				return '8{0}{1}1 - Sets V{0} to (V{0} or V{1}).'.format(hex(a)[-1], hex(b)[-1])
			elif c == 2:
				self.v[a] = (self.v[a] & self.v[b])
				return '8{0}{1}2 - Sets V{0} to (V{0} and V{1}).'.format(hex(a)[-1], hex(b)[-1])
			elif c == 3:
				self.v[a] = (self.v[a] ^ self.v[b])
				return '8{0}{1}3 - Sets V{1} to (V{0} xor V{1}).'.format(hex(a)[-1], hex(b)[-1])
			elif c == 4:
				if (self.v[a] + self.v[b]) > 0xFF:
					self.v[15] = 1
					self.v[b] += self.v[a]
					self.v[b] -= 0xFF
				else:
					self.v[b] += self.v[a]
					self.v[15] = 0
				return '8{0}{1}4 - Adds V{0} to V{1}. VF is set to 1 when there\'s a carry, and to 0 when there isn\'t.'.format(hex(a)[-1], hex(b)[-1])
			elif c == 5:
				if (self.v[a] - self.v[b]) < 0x00:
					self.v[15] = 0
					self.v[a] -= self.v[b]
					self.v[a] += 0xFF + self.v[a]
				else:
					self.v[a] -= self.v[b]
					self.v[15] = 1
				return '8{0}{1}5 - V{1} is subtracted from V{0}. VF is set to 0 when there\'s a borrow, and 1 when there isn\'t'.format(hex(a)[-1], hex(b)[-1])
			elif c == 6:
				self.v[15] = (self.v[a] & 1)
				self.v[a] = (self.v[a] >> 1)
				return '8{0}{1}6 - Shifts V{0} right by one. VF is set to the value of the least significant bit of V{0} before the shift.'.format(hex(a)[-1], hex(b)[-1])
			elif c == 7:
				if (self.v[b] - self.v[a]) < 0x00:
					self.v[15] = 0
					self.v[a] -= self.v[b]
					self.v[a] += 0xFF + self.v[a]
				else:
					self.v[15] = 1
					self.v[b] = (self.v[b] - self.v[a]) & 0xFF
				return '8{0}{1}7 - Sets V{0} to (V{1} minus V{0}). VF is set to 0 when there\'s a borrow, and 1 when there isn\'t.'.format(hex(a)[-1], hex(b)[-1])
			elif c == 15:
				self.v[15] = (self.v[a] & 1)
				self.v[a] = (self.v[a] << 1)
				return '8{0}{1}E - Shifts V{0} left by one. VF is set to the value of the most significant bit of V{0} before the shift.'.format(hex(a)[-1], hex(b)[-1])
			else:
				return "invalid opcode"
		elif (op == 9 and command[4] == 0):
			if self.v[a] != self.v[b]:
				self.pc += 2
			return '9{0}{1}0 - Skips the next instruction if V{0} doesn\'t equal V{1}.'.format(hex(a)[-1], hex(b)[-1])
		elif op == 10:
			self.i = insn & 0xFFF
			return 'A{0}{1}{2} - Set I to address 0x{0}{1}{2}.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 11:
			self.pc = (insn & 0xFFF) + self.v[0]
			return 'B{0}{1}{2} - Jumps to the address (0x{0}{1}{2} plus V0 (not necessarily V{0})).'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1]) # hooray, mixed addition!
		elif op == 12:
			self.v[a] = (randrange(0, 256) & (insn & 0xFF))
			return 'C{0}{1}{2} - Sets V{0} to (a random number & {1}{2}).'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 13:
			s_array = self.create_sprite_array(c)
			self.draw_sprite(s_array, self.v[a], self.v[b])
			return 'D{0}{1}{2} - Draws a sprite at coordinate (V{0:x}, V{1:x}) that has a width of 8 pixels and a height of {2:x} pixels. Each row of 8 pixels is read as bit-coded (with the most significant bit of each byte displayed on the left) starting from memory location I; I value doesn\'t change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that doesn\'t happen.'.format(a, b, c)
			# return 'D{0}{1}{2} - Draws a sprite at coordinate (V{0}, V{1}) that has a width of 8 pixels and a height of {2} pixels. Each row of 8 pixels is read as bit-coded (with the most significant bit of each byte displayed on the left) starting from memory location I; I value doesn\'t change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that doesn\'t happen.'.format(hex(a)[-1], hex(b)[-1], hex(c)[-1])
		elif op == 14:
			if (b == 9 and c == 15):
				# TODO: Figure out how to record key presses.
				return 'E{0}9E - Skips the next instruction if the key stored in V{0} is pressed.'.format(hex(a)[-1])
			elif (b == 10 and c == 1):
				# TODO: Figure out how to record key presses.
				return 'E{0}A1 - Skips the next instruction if the key stored in V{0} isn\'t pressed.'.format(hex(a)[-1])
			else:
				return 'invalid opcode'
		elif op == 15:
			if (b == 0 and c == 7):
				# TODO: Understand and create delay timer.
				return 'F{0}07 - Set V{0} to value of delay timer.'.format(hex(a)[-1])
			elif (b == 0 and c == 10):
				# TODO: Figure out how to record key presses.
				return 'F{0}0A - A key press is awaited, and then stored in V{0}.'.format(hex(a)[-1])
			elif (b == 1 and c == 5):
				return 'F{0}15 - Set delay timer to V{0}.'.format(hex(a)[-1])
			elif (b == 1 and c == 8):
				return 'F{0}18 - Set sound timer to V{0}.'.format(hex(a)[-1])
			elif (b == 1 and c == 15):
				return 'F{0}1E - Add V{0} to I.'.format(hex(a)[-1])
			elif (b == 2 and c == 9):
				return 'F{0}29 - Set I to the location of the sprite for the character in V{0}. Characters 0-F (in hexadecimal) are represented by a 4x5 font.'.format(hex(a)[-1])
			elif (b == 3 and c == 3):
				return 'F{0}33 - Store the Binary-coded decimal representation of V{0}, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of V{0}, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.)'.format(hex(a)[-1])
				# that last one looks like a huge pain in the ass...
			elif (b == 5 and c == 5):
				return 'F{0}55 - Store V0 to V{0} in memory starting at address I.'.format(hex(a)[-1])
			elif (b == 6 and c == 5):
				return 'F{0}65 - Fill V0 to V{0} with values from memory starting at address I.'.format(hex(a)[-1])
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

chip = Chip8()



chip.run_program(program)