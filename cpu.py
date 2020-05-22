import sys

LDI = 130
PRN = 71
HLT = 1
MUL = 162
PUSH = 69
POP = 70
# Add CMP
CMP = 167
# Add JMP, JEQ, JNE
JMP = 84
JEQ = 85
JNE = 86

# Implement the CPU constructor
class CPU:
	def __init__(self):
		"""Construct A New CPU"""
		self.ram = [0] * 256
		self.register = [0] * 8
		self.pc = 0
		self.register[7] = 0xF4
		self.sp = 7
		self.equal = {}
		# Construct a branch table - create a dictionary for the branch table
		self.branch_table = {}
		self.branch_table[LDI] = self.ldi
		self.branch_table[PRN] = self.prn
		self.branch_table[MUL] = self.mul
		self.branch_table[PUSH] = self.push
		self.branch_table[POP] = self.pop
		self.branch_table[CMP] = self.cmp
		self.branch_table[JMP] = self.jmp
		self.branch_table[JEQ] = self.jeq
		self.branch_table[JNE] = self.jne

	# takes file input
	def load(self):
		"""Load a program into memory."""
		address = 0

    # Un-hardcode the machine code 
    # Open a file
		with open(sys.argv[1]) as file:
			for instruction in file:
                # clean the instructions of empty space
				cleaned_instruction = instruction.split(" ")[0]
                # clean the instructions of '#'
				if cleaned_instruction != "#":
                    # then we load it into memory
					self.ram[address] = int(cleaned_instruction, 2) # keeping it in binary
                    # then move onto the next
					address += 1

	# ALU to perform arithmatic operations and also CMP operations
	def alu(self, op, reg_a, reg_b):
		"""ALU operations."""

		# variables to be used for flagging
		a = self.register[reg_a]
		b = self.register[reg_b]

		if op == "ADD":
			self.register[a] += self.register[b]
		elif op == "MUL":
			self.register[a] *= self.register[b]
		elif op == "CMP":
			# If they are equal, set the Equal E flag to 1, otherwise set it to 0.
			if a == b:
				self.flags["E"] = 1
			else:
				self.flags["E"] = 0
			# If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
			if a < b:
				self.flags["L"] = 1
			else:
				self.flags["L"] = 0
			# If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
			if a > b:
				self.flags["G"] = 1
			else:
				self.flags["G"] = 0

		else:
			raise Exception("Unsupported ALU operation")

    # Add RAM functions:
    # ram_read() - should accept the address to read and return the value stored there.
    # ram_write() - should accept a value to write, and the address to write it to.

	def read_ram(self, MAR):
		return self.ram[MAR]

	def write_ram(self, MAR, MDR):
		self.ram[MAR] = MDR

    # Add the LDI instruction
    # load "immediate", store a value in a register, or "set this register to this value".
	def ldi(self, operand_a, operand_b):
		self.register[operand_a] = operand_b

    # Add the PRN instruction
    # a pseudo-instruction that prints the numeric value stored in a register.
	def prn(self, operand_a, operand_b):
		print(self.register[operand_a])
    
    # Implement the HLT instruction handler
    # halt the CPU and exit the emulator.
    # def HLT(self):
    #    self.halted = True

    # Implement the MUL instruction handler
    # mul operation multiplies
	def mul(self, operand_a, operand_b):
		self.alu("MUL", operand_a, operand_b)

    # Implement the PUSH instruction handler
    # push operation adds an element to the stack
	def push(self, operand_a, operand_b):
		self.register[self.sp] -= 1
		val = self.register[operand_a]
		self.write_ram(self.register[self.sp], val)

    # Implement the POP instruction handler
    # pop operation removes an element from the top position.
	def pop(self, operand_a, operand_b):
		val = self.read_ram(self.register[self.sp])
		self.register[operand_a] = val
		self.register[self.sp] += 1
	
	# Implement the CMP instruction
	# CMP compares two operands
	def cmp(self, operand_a, operand_b):
		self.alu("CMP", operand_a, operand_b)

	# Implement JMP instruction
	# JMP Jumps to the address stored in the given register.
	def jmp(self, operand_a, operand_b):
		# Set the PC to the address stored in the given register.
		self.pc = self.register[operand_a]

	# Implement the JEQ instruction
	# JEQ job is if equal flag is set (true), jump to the address stored in the given register.
	def jeq(self, operand_a, operand_b):
		if self.flags["E"] == 1:
			self.pc = self.register[operand_a]
		else:
			# if not, jump onto the 2nd
			self.pc += 2

	# Implement the JNE instruction
	# JNE is if E flag is clear (false, 0), jump to the address stored in the given register.
	def jne(self, operand_a, operand_b):
		if self.flags["E"] == 0:
			self.pc = self.register[operand_a]
		else:
			# if not jump onto the 2nd
			self.pc += 2

    # Implement the core of run()
	def run(self):
		"""Run The CPU"""

        # not ending
		halted = False

        # if its not ending
		while not halted:
            # Instruction Register - is the register which holds the instruction which is currently been executed.
            # instruction register will look through the ram to then know which pointer to be at
			IR = self.read_ram(self.pc)
            # PC+1 and PC+2 from RAM into variables operand_a and operand_b
			operand_a = self.read_ram(self.pc + 1)
			operand_b = self.read_ram(self.pc + 2)

            # If the instruction register is ending
			if IR == HLT:
                # then end
				halted = True
            # or if the IR has an instruction to do
			elif IR in self.branch_table:
                # the instructions are in the branch_table
                # it will then run through operand_a and operand_b
				self.branch_table[IR](operand_a, operand_b)
				self.pc += (IR >> 6) + 1
			else:
				print("Instruction not recognized")
				sys.exit(1)