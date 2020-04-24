"""CPU functionality."""

import sys

#means 0b bits, the machine language instruction
POP = 0b01000110
PUSH = 0b01000101 #01000101 00000rrr

HLT = 0b00000001 #01000101 00000rrr
LDI = 0b10000010
PRN = 0b01000111

#Math operation
MUL = 0b10100010
ADD = 0b10100000
CMP = 0b10100111

AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100100

JUMP = 0b01010100
CALL = 0b01010000

JNE = 0b01010110
JEQ = 0b01010101

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.Registers =  [0]*8
        #internal registers
        self.pc=0 #program Counter
        self.flag=0
        #make a dictionary to handle instruction
        #these are the defaults registry.
        self.InstructionTable = {}
        self.InstructionTable[PUSH] = self.push
        self.InstructionTable[POP] = self.pop

        self.InstructionTable[HLT] = self.InterruptThenQuit_HLT
        self.InstructionTable[LDI] = self.MemoryAddressRegister_LDI # set specific registry to value
        self.InstructionTable[PRN] = self.MemoryDataRegister_PRN

        #math operation
        self.InstructionTable[MUL] = self.Function_MUL # mulitply
        self.InstructionTable[ADD] = self.Function_add
        self.InstructionTable[CMP] = self.Function_CMP
        self.InstructionTable[AND] = self.Function_AND
        self.InstructionTable[OR] = self.Function_OR
        self.InstructionTable[XOR] = self.Function_XOR
        self.InstructionTable[NOT] = self.Function_NOT
        self.InstructionTable[SHL] = self.Function_SHL
        self.InstructionTable[SHR] = self.Function_SHR
        self.InstructionTable[MOD] = self.Function_MOD

        self.InstructionTable[CALL] = self.handle_call
        self.InstructionTable[JUMP] = self.handle_jump

        self.InstructionTable[JEQ] = self.jeq
        self.InstructionTable[JNE] = self.jne

        self.sp=7 #r7 is reserve for this stackpointer
        self.Registers[self.sp] = 0xf4 #value of key pressed

    def push(self, *operands):
        #increment register, get register number and value.
        #apply the
        self.Registers[self.sp] -= 1
        reg_num = self.ram[self.pc+1]
        reg_value=self.Registers[reg_num]
        #get address
        address = self.Registers[self.sp]
        self.ram[address]=reg_value
        self.pc+=2
    #pop the address to register immediantly for cpu
    def pop(self, *operands):
        #get register Number, and address at ram
        register_value = self.ram[self.Registers[self.sp]]
        address = self.ram[self.pc+1]
        self.Registers[address] = register_value #the ram will be assign such that the CPU can process this.
        self.Registers[self.sp]+=1
        self.pc+=2

    #accept the address to read and return the value stored there
    def ram_read(self, address):
        return self.ram[address]

    #accept a value to write, and the address to write it to,.
    def ram_write(self, value, address):
        self.ram[address] = value #go to the ram which holds the address, then grab the value there. in python assign value to ram[address]

    def load(self):
        if len(sys.argv) != 2:
            print("Usage: file.py filename", file=sys.stderr)
            sys.exit(1)
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    # Ignore comments
                    comment_split = line.split("#")
                    num = comment_split[0].strip()
                    if num == "":
                        continue  # Ignore blank lines
                    value = int(num, 2)   # Base 10, but ls-8 is base 2
                    self.ram[address] = value
                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)
    def alu(self, operation, operand_a, operand_b):
        """At CMP, if OP A = OP B, then Flag= 0,
                   if OP A < OP B then Flag = 1
                   if OP A > OP B then Flag = 1"""
        if operation == "ADD":
            self.Registers[operand_a]+=self.Registers[operand_b]
        elif operation == "MUL":
            self.Registers[operand_a]*=self.Registers[operand_b]
        elif operation == "CMP":
            if self.Registers[operand_a] == self.Registers[operand_b]:
                self.flag = 0b00000001
            elif self.Registers[operand_a] < self.Registers[operand_b]:
                self.flag = 0b00000100
            elif self.Registers[operand_a] > self.Registers[operand_b]:
                self.flag = 0b00000010
        elif operation == "AND":
            self.Registers[operand_a] &= self.Registers[operand_b]
        elif operation == "OR":
            self.Registers[operand_a] |= self.Registers[operand_b]
        elif operation =="XOR":
            self.Registers[operand_a] ^= self.Registers[operand_b]
        elif operation == "NOT":
            self.Registers[operand_a] = ~self.reg[operand_b]
        elif operation == "SHL": #shift to left
            self.Registers[operand_a] = self.Registers[operand_a] <<  operand_a
        elif operation == "SHR": #shift to right
            self.Registers[operand_a] = self.Registers[operand_a] >> operand_b
        elif operation == "MOD": #store the remainder in register A
            self.Registers[operand_a] %= self.Registers[operand_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.Registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        print('running...')
        self.trace()
        looping = True
        while(looping):
            address = self.ram_read(self.pc) #
            operand_count = (address >> 6) & 0b00000011
            #print(operand_count, 'testing address')
            operands = []
            for i in range(1, operand_count + 1):
                operands.append(self.ram_read(self.pc + i))
            if address in self.InstructionTable:
                self.InstructionTable[address](operands)
            else:
                print("Instruction not found!")
                looping=False

    def push(self, *operands):
        # increment register, get register number and value.
        # apply the
        self.Registers[self.sp] -= 1
        reg_num = self.ram[self.pc + 1]
        reg_value = self.Registers[reg_num]
        # get address
        address = self.Registers[self.sp]
        self.ram[address] = reg_value
        self.pc += 2
        # pop the address to register immediantly for cpu

    def pop(self, *operands):
        # get register Number, and address at ram
        register_value = self.ram[self.Registers[self.sp]]
        address = self.ram[self.pc + 1]
        self.Registers[address] = register_value  # the ram will be assign such that the CPU can process this.
        self.Registers[self.sp] += 1
        self.pc += 2

    #
    def InterruptThenQuit_HLT(self, operand):
        print("quitting")
        self.looping=False
        sys.exit(1)#Error ExitsStatus.

    def MemoryAddressRegister_LDI(self, operand):
        #LDI register immediate - set the value of a register to an integer
        #so do i need to loop up interger?
        #am i assigning this spot to hold enought information for an type() int, byte, unicode
        # or am i setting the value to a string.
        #print('accessing memory address register')
        self.Registers[operand[0]] = operand[1]
        self.pc += 3

    def MemoryDataRegister_PRN(self, operand ):
        print(self.Registers[operand[0]], 'accessing memoryData Register')
        self.pc+=2



    #handles operation Muliply, comparing, adding
    def Function_MUL(self,operand):
        self.alu("MUL", operand[0], operand[1])
        self.pc+=3

    def Function_CMP(self, operands):
        self.alu("CMP", operands[0], operands[1])
        self.pc += 3

    def Function_add(self, operands):
        self.alu("ADD", operands[0], operands[1])
        self.pc += 3

    def Function_AND(self, operands):
        self.alu("AND", operands[0], operands[1])
        self.pc += 3

    def Function_OR(self, operands):
        self.alu("OR", operands[0], operands[1])

    def Function_XOR(self, operand):
        self.alu("XOR", operand[0], operand[1])
        self.pc += 3

    def Function_NOT(self, operands):
        self.alu("NOT", operands[0], operands[1])
        self.pc += 3

    def Function_SHL(self, operands):
        self.alu("SHL", operands[0], operands[1])
        self.pc += 3

    def Function_SHR(self, operands):
        self.alu("SHR", operands[0], operands[1])
        self.pc += 3

    def Function_MOD(self, operands):
        self.alu("OR", operands[0], operands[1])


    def handle_call(self, operand):
        print('call') # push address to stack, then set pc to "VALUE" register
        address = self.Registers[self.sp] - 1
        self.ram[self.Registers[self.sp]] =  self.pc + 2
        #set pc to value register
        register_number = self.ram[self.pc +1]
        self.pc = self.Registers[register_number] #

    def handle_jump(self, operand):
        print('call,')
        #set the pc to the address stored in given register
        self.pc = self.Registers[operand[0]]

    def jeq(self, operands):
        print('equal flag is true, jump to address stored in given register')
        if(self.flag & 0b00000001 ) ==1:
            self.pc = self.Registers[operands[0]]
        else:
            self.pc+=2
    def jne(self, operands):
        if(self.flag & 0b00000001 ) == 0:
            self.pc = self.Registers[operands[0]]
        else:
            self.pc+=2