from src import chip8
import random

def setup():
    print("Setup!")
    global my_chip8
    my_chip8 = chip8.Chip8()
    my_chip8.initialise()

def teardown():
    print("Setup!")

def test_0NNN():
    # Calls RCA 1802 program at address NNN
    # I don't think this is being used for the time being, so it this
    # test will fail. I might implement it at a later date.
    # The RCA 1802 is a CPU, so I suspect this is sort of like the Amiga
    # calling PowerPC instructions from an expansion card.
    my_chip8.reset()
    my_chip8.memory[0x200] = 0x0F
    my_chip8.memory[0x201] = 0xFF
    my_chip8.emulate_cycle()


# Clear the screen
# Set the video memory to random data, and then test the opcode to
# Clear it.
def test_00E0():
    # Re-initialise the system
    my_chip8.reset()
    # create a random number generator
    new_random = random.Random()
    # We want out test to be predictable. Force a seed.
    new_random.seed(123)
    for i in range(0, 64 * 32):
        # Write to our video memory random pixels
        my_chip8.graphics[i] = new_random.randint(0,1)
    # The program starts at 0x200, so set the 2 opcodes
    my_chip8.memory[0x200] = 0x00
    my_chip8.memory[0x201] = 0xE0
    my_chip8.emulate_cycle()
    # The program counter wants to have incremented, else we will be
    # clearing the screen forever
    assert my_chip8.program_counter == 0x202
    assert my_chip8.graphics == [0] * (64 * 32)

# Returns from a subroutine
# Need to make sure we move to the correct memory address, and the stack
# pointer changes
def test_00EE_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.stack[0] = 0x206
    my_chip8.stack_pointer = 1
    # The program starts at 0x200, so set the 2 opcodes
    my_chip8.memory[0x200] = 0x00
    my_chip8.memory[0x201] = 0xEE
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x208
    assert my_chip8.stack_pointer == 0

# Returns from a subroutine
# Need to make sure we move to the correct memory address, and the stack
# pointer changes
def test_00EE_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.stack[9] = 0x636
    my_chip8.stack_pointer = 0xA
    # The program starts at 0x200, so set the 2 opcodes
    my_chip8.memory[0x200] = 0x00
    my_chip8.memory[0x201] = 0xEE
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x638
    assert my_chip8.stack_pointer == 9

# Jumps to address NNN
# Move to the correct memory address and do not increment
def test_1NNN():
    # Re-initialise the system
    my_chip8.reset()
    my_chip8.memory[0x200] = 0x15
    my_chip8.memory[0x201] = 0x23
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x523

# Calls subroutine at NNN
# Move to the correct memory address and do not increment and store old place
def test_2NNN():
    # Re-initialise the system
    my_chip8.reset()
    my_chip8.memory[0x200] = 0x25
    my_chip8.memory[0x201] = 0x23
    my_chip8.emulate_cycle()
    assert my_chip8.stack_pointer == 1
    assert my_chip8.stack[0] == 0x200
    assert my_chip8.program_counter == 0x523

# Skips to the next instruction if VX equals NN
def test_3XNN_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[4] = 0x23
    my_chip8.memory[0x200] = 0x34
    my_chip8.memory[0x201] = 0x23
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x204

# Skips to the next instruction if VX equals NN
def test_3XNN_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[4] = 0x21
    my_chip8.memory[0x200] = 0x34
    my_chip8.memory[0x201] = 0x23
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202

# Skips to the next instruction if VX doesn't equals NN
def test_4XNN_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[4] = 0x23
    my_chip8.memory[0x200] = 0x44
    my_chip8.memory[0x201] = 0x23
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202

# Skips to the next instruction if VX doesn't equals NN
def test_4XNN_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[4] = 0x21
    my_chip8.memory[0x200] = 0x44
    my_chip8.memory[0x201] = 0x23
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x204

# Skips to the next instruction if VX equals VY
def test_5XY0_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x23
    my_chip8.v[4] = 0x23
    my_chip8.memory[0x200] = 0x54
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x204

# Skips to the next instruction if VX equals VY
def test_5XY0_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x22
    my_chip8.v[4] = 0x21
    my_chip8.memory[0x200] = 0x54
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202

# Sets VX to NN
def test_6XNN():
    # Re-initialise the system
    my_chip8.reset()
    my_chip8.memory[0x200] = 0x64
    my_chip8.memory[0x201] = 0x35
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.v[4] == 0x35

# Adds NN to VX
def test_7XNN_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[4] = 0x22
    my_chip8.memory[0x200] = 0x74
    my_chip8.memory[0x201] = 0x35
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.v[4] == 0x57

# Adds NN to VX
def test_7XNN_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[4] = 0xFF
    my_chip8.memory[0x200] = 0x74
    my_chip8.memory[0x201] = 0xFF
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.v[4] == 0xFE

# Sets VX to the value of VY
def test_8XY0():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0xFE
    my_chip8.v[4] = 0x00
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0xFE
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0xFE
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0XF] == 0x00
    assert my_chip8.program_counter == 0x202

# Sets VX to the value of VX OR VY (bitwise OR)
def test_8XY1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x24
    my_chip8.v[4] = 0x63
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x21
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x24
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x67
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0XF] == 0x00
    assert my_chip8.program_counter == 0x202

# Sets VX to the value of VX AND VY (bitwise AND)
def test_8XY2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x24
    my_chip8.v[4] = 0x63
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x22
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x24
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x20
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0XF] == 0x00
    assert my_chip8.program_counter == 0x202

# Sets VX to the value of VX XOR VY (bitwise XOR)
def test_8XY3():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x24
    my_chip8.v[4] = 0x63
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x23
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x24
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x47
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0XF] == 0x00
    assert my_chip8.program_counter == 0x202

# Adds VY to VX. VF is set to 1 when there's a carry, and 0 when there isn't
def test_8XY4_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x24
    my_chip8.v[4] = 0x64
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x24
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x24
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x88
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0XF] == 0x00
    assert my_chip8.program_counter == 0x202

# Adds VY to VX. VF is set to 1 when there's a carry, and 0 when there isn't
def test_8XY4_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x84
    my_chip8.v[4] = 0x84
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x24
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x84
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x08
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0XF] == 0x1
    assert my_chip8.program_counter == 0x202

# Subtracts VY from VX. VF is set to 0 when there's a borrow, and 1 when there isn't
def test_8XY5_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x24
    my_chip8.v[4] = 0x64
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x25
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x24
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x40
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0xF] == 0x1
    assert my_chip8.program_counter == 0x202

# Subtracts VY from VX. VF is set to 0 when there's a borrow, and 1 when there isn't
def test_8XY5_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x64
    my_chip8.v[4] = 0x24
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x25
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x64
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0xC0
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0xF] == 0x0
    assert my_chip8.program_counter == 0x202

def test_8XY6_1():
    # Re-initialise the system
    my_chip8.reset()
    # Shifts VX right by one. VF is set to the least significant bit of VX before the shift
    my_chip8.v[4] = 0x03
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x26
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x00
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x01
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0xF] == 0x1
    assert my_chip8.program_counter == 0x202

def test_8XY6_2():
    # Re-initialise the system
    my_chip8.reset()
    # Shifts VX right by one. VF is set to the least significant bit of VX before the shift
    my_chip8.v[4] = 0x02
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x26
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x00
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x01
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0xF] == 0x0
    assert my_chip8.program_counter == 0x202

# Sets VX to VY - VX. VF is set to 0 when there is a borrow, and 1 when there isn't
def test_8XY7_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x24
    my_chip8.v[4] = 0x64
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x27
    my_chip8.emulate_cycle()
    assert my_chip8.v[4] == 0xC0
    assert my_chip8.v[0xF] == 0x0
    assert my_chip8.program_counter == 0x202

# Sets VX to VY - VX. VF is set to 0 when there is a borrow, and 1 when there isn't
def test_8XY7_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x64
    my_chip8.v[4] = 0x24
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x27
    my_chip8.emulate_cycle()
    assert my_chip8.v[4] == 0x40
    assert my_chip8.v[0xF] == 0x1
    assert my_chip8.program_counter == 0x202

def test_8XYE_1():
    # Re-initialise the system
    my_chip8.reset()
    # Shifts VX right by one. VF is set to the least significant bit of VX before the shift
    my_chip8.v[4] = 0x01
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x2E
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x00
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x02
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0xF] == 0x0
    assert my_chip8.program_counter == 0x202

def test_8XYE_2():
    # Re-initialise the system
    my_chip8.reset()
    # Shifts VX right by one. VF is set to the least significant bit of VX before the shift
    my_chip8.v[4] = 0x81
    my_chip8.memory[0x200] = 0x84
    my_chip8.memory[0x201] = 0x2E
    my_chip8.emulate_cycle()
    assert my_chip8.v[0] == 0x00
    assert my_chip8.v[1] == 0x00
    assert my_chip8.v[2] == 0x00
    assert my_chip8.v[3] == 0x00
    assert my_chip8.v[4] == 0x02
    assert my_chip8.v[5] == 0x00
    assert my_chip8.v[6] == 0x00
    assert my_chip8.v[7] == 0x00
    assert my_chip8.v[8] == 0x00
    assert my_chip8.v[9] == 0x00
    assert my_chip8.v[0XA] == 0x00
    assert my_chip8.v[0XB] == 0x00
    assert my_chip8.v[0XC] == 0x00
    assert my_chip8.v[0XD] == 0x00
    assert my_chip8.v[0XE] == 0x00
    assert my_chip8.v[0xF] == 0x1
    assert my_chip8.program_counter == 0x202

# Skips to the next instruction if VX doesn't equal VY
def test_9XY0_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x23
    my_chip8.v[4] = 0x23
    my_chip8.memory[0x200] = 0x94
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202

# Skips to the next instruction if VX doesn't equal VY
def test_9XY0_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[2] = 0x22
    my_chip8.v[4] = 0x21
    my_chip8.memory[0x200] = 0x94
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x204

# Sets I to NNN
def test_ANNN():
    # Re-initialise the system
    my_chip8.reset()
    my_chip8.memory[0x200] = 0xA4
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.i == 0x420

# Sets I to NNN plus V0
def test_BNNN():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x0] = 0x44
    my_chip8.memory[0x200] = 0xB4
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.i == 0x464

# Sets VX to a random number AND NN (Assuming bitwise AND. Not really
# sure about testing this as what is significant about a random number?)
def test_CXNN():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.test_rand = True
    ran = random.Random()
    ran.seed(123)
    my_chip8.memory[0x200] = 0xC4
    my_chip8.memory[0x201] = 0x20
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.v[0x4] == (0x20 & ran.randint(0x0, 0xFF))

# Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels
# and a height of N pixels. Each row of 8 pixels is read as bit-coded
# (with the most significant bit of each byte displayed on the left)
# starting from memory location I. I value doesn't change after the
# execution of this instruction. VF is set to 1 if any pixels are
# flipped from set to unset when the sprite is drawn, and 0 if not
def test_DXYN():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0x08
    my_chip8.v[0x2] = 0x05
    my_chip8.i = 0x032 # Start of A, I hope
    mock_screen = [0] * (32 * 64)
    mock_screen[328] = mock_screen[329] = mock_screen[330] = mock_screen[331] = 1
    mock_screen[392] = mock_screen[395] = 1
    mock_screen[456] = mock_screen[457] = mock_screen[458] = mock_screen[459] = 1
    mock_screen[520] = mock_screen[523] = 1
    mock_screen[584] = mock_screen[587] = 1
    my_chip8.memory[0x200] = 0xD4
    my_chip8.memory[0x201] = 0x25
    my_chip8.emulate_cycle()
    assert my_chip8.v[0xF] == 0
    assert my_chip8.program_counter == 0x202
    assert my_chip8.graphics == mock_screen

# Skips the next instruction if the key stored in VX is pressed
def test_EX9E_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0x08
    my_chip8.key[0x8] = 0x1
    my_chip8.memory[0x200] = 0xE4
    my_chip8.memory[0x201] = 0x9E
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x204

# Skips the next instruction if the key stored in VX is pressed
def test_EX9E_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0x08
    my_chip8.key[0x8] = 0x0
    my_chip8.memory[0x200] = 0xE4
    my_chip8.memory[0x201] = 0x9E
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202

# Skips the next instruction if the key stored in VX isn't pressed
def test_EXA1_1():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0x08
    my_chip8.key[0x8] = 0x1
    my_chip8.memory[0x200] = 0xE4
    my_chip8.memory[0x201] = 0xA1
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202

# Skips the next instruction if the key stored in VX isn't pressed
def test_EXA1_2():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0x08
    my_chip8.key[0x8] = 0x0
    my_chip8.memory[0x200] = 0xE4
    my_chip8.memory[0x201] = 0xA1
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x204

# Sets VX to the value of the delay timer
def test_FX07():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[4] = 0x00
    my_chip8.delay_timer = 0xFF
    my_chip8.memory[0x200] = 0xF4
    my_chip8.memory[0x201] = 0x07
    my_chip8.emulate_cycle()
    assert my_chip8.v[4] == 0xFF
    assert my_chip8.program_counter == 0x202

def test_FX0A():
    # A key press is awaited, and then stored in VX
    my_chip8.opcode = 0xFF0A
    my_chip8.emulate_cycle()
    pass

# Sets the delay timer to VX
def test_FX15():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0xFF
    my_chip8.delay_timer = 0x00
    my_chip8.memory[0x200] = 0xF4
    my_chip8.memory[0x201] = 0x15
    my_chip8.emulate_cycle()
    # Emulate cycle de-increments the timers at the end. We need to show
    # this
    assert my_chip8.delay_timer == 0xFF - 0x01
    assert my_chip8.program_counter == 0x202

# Sets the sound timer to VX
def test_FX18():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0xFF
    my_chip8.sound_timer = 0x00
    my_chip8.memory[0x200] = 0xF4
    my_chip8.memory[0x201] = 0x18
    my_chip8.emulate_cycle()
    # Emulate cycle de-increments the timers at the end. We need to show
    # this
    assert my_chip8.sound_timer == 0xFF - 0x01
    assert my_chip8.program_counter == 0x202

# Adds VX to I
def test_FX1E():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0x04
    my_chip8.i = 0x244
    my_chip8.memory[0x200] = 0xF4
    my_chip8.memory[0x201] = 0x1E
    my_chip8.emulate_cycle()
    assert my_chip8.i == 0x248
    assert my_chip8.program_counter == 0x202

# Sets I to the location of the sprite for the character in VX
def test_FX29():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.v[0x4] = 0xA
    my_chip8.memory[0x200] = 0xF4
    my_chip8.memory[0x201] = 0x29
    my_chip8.emulate_cycle()
    assert my_chip8.i == 0x032
    assert my_chip8.program_counter == 0x202

# Stores the binary coded decimal representation of VX, with the
# most significant of three digits at the address in I, the middle
# digit at I plus 1, and the least significant digit at I plus 2.
def test_FX33():
    my_chip8.opcode = 0xFF33
    my_chip8.emulate_cycle()
    pass

# Stores V0 to VX in memory starting at address I
def test_FX55():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.i = 0x400
    my_chip8.v[0x0] = 0xDE
    my_chip8.v[0x1] = 0xAD
    my_chip8.v[0x2] = 0xBE
    my_chip8.v[0x3] = 0xEF
    my_chip8.memory[0x200] = 0xF3
    my_chip8.memory[0x201] = 0x55
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.memory[0x400] == 0xDE
    assert my_chip8.memory[0x401] == 0xAD
    assert my_chip8.memory[0x402] == 0xBE
    assert my_chip8.memory[0x403] == 0xEF

# Fills V0 to VX with values from memory starting at address I
def test_FX65():
    # Re-initialise the system
    my_chip8.reset()
    # Set up mock situation
    my_chip8.i = 0x400
    my_chip8.memory[0x400] = 0xDE
    my_chip8.memory[0x401] = 0xAD
    my_chip8.memory[0x402] = 0xBE
    my_chip8.memory[0x403] = 0xEF
    my_chip8.memory[0x200] = 0xF3
    my_chip8.memory[0x201] = 0x65
    my_chip8.emulate_cycle()
    assert my_chip8.program_counter == 0x202
    assert my_chip8.v[0x0] == 0xDE
    assert my_chip8.v[0x1] == 0xAD
    assert my_chip8.v[0x2] == 0xBE
    assert my_chip8.v[0x3] == 0xEF
