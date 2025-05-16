#!/bin/env python
#####
#
# Chip 8 emulator
#
# Inspiration (a little help on a few opcodes) from http://www.multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
# List of opcodes and more information - https://en.wikipedia.org/wiki/CHIP-8#Virtual_machine_description
# Function pointers - http://www.multigesture.net/wp-content/uploads/mirror/zenogais/FunctionPointers.htm
#
#####
import sys
import numpy
import random

class Chip8:
    screen_width = 64
    screen_height = 32
    ops_per_second = 60

    fontset = [0xf0, 0x90, 0x90, 0x90, 0xf0, # 0
               0x20, 0x60, 0x20, 0x20, 0x70, # 1
               0xf0, 0x10, 0xf0, 0x80, 0xf0, # 2
               0xf0, 0x10, 0xf0, 0x10, 0xf0, # 3
               0x90, 0x90, 0xf0, 0x10, 0x10, # 4
               0xf0, 0x80, 0xf0, 0x10, 0xf0, # 5
               0xf0, 0x80, 0xf0, 0x90, 0xf0, # 6
               0xf0, 0x10, 0x20, 0x40, 0x40, # 7
               0xf0, 0x90, 0xf0, 0x90, 0xf0, # 8
               0xf0, 0x90, 0xf0, 0x10, 0xf0, # 9
               0xf0, 0x90, 0xf0, 0x90, 0x90, # A
               0xe0, 0x90, 0xe0, 0x90, 0xe0, # B
               0xf0, 0x80, 0x80, 0x80, 0xf0, # C
               0xe0, 0x90, 0x90, 0x90, 0xe0, # D
               0xf0, 0x80, 0xf0, 0x80, 0xf0, # E
               0xf0, 0x80, 0xf0, 0x80, 0x80] # F

    def initialise(self):
        print("Initialising")
        self.reset()
        self.setup_opcode_pointers()

    def setup_opcode_pointers(self):
        self.chip8_table = [self.cpu0xxx, self.cpu1xxx, self.cpu2xxx,
                            self.cpu3xxx, self.cpu4xxx, self.cpu5xxx,
                            self.cpu6xxx, self.cpu7xxx, self.cpu8xxx,
                            self.cpu9xxx, self.cpuAxxx, self.cpuBxxx,
                            self.cpuCxxx, self.cpuDxxx, self.cpuExxx,
                            self.cpuFxxx]
        self.chip8_system = [self.cpu00E0, self.cpuNULL, self.cpuNULL,
                             self.cpuNULL, self.cpuNULL, self.cpuNULL,
                             self.cpuNULL, self.cpuNULL, self.cpuNULL,
                             self.cpuNULL, self.cpuNULL, self.cpuNULL,
                             self.cpuNULL, self.cpuNULL, self.cpu00EE,
                             self.cpuNULL]
        self.chip8_arithmetic = [self.cpu8xx, self.cpu8xx1, self.cpu8xx2,
                                 self.cpu8xx3, self.cpu8xx4, self.cpu8xx5,
                                 self.cpu8xx6, self.cpu8xx7, self.cpuNULL,
                                 self.cpuNULL, self.cpuNULL, self.cpuNULL,
                                 self.cpuNULL, self.cpuNULL, self.cpu8xxE,
                                 self.cpuNULL]
        self.chip8_skip = [self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuEx9x, self.cpuExAx, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL]
        self.chip8_misc = [self.cpuFxx, self.cpuFx1x, self.cpuFx2x,
                           self.cpuFx3x, self.cpuNULL, self.cpuFx5x,
                           self.cpuFx6x, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL]
        self.chip8_fxn = [self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuFx7, self.cpuNULL,
                           self.cpuNULL, self.cpuFxA, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL]
        self.chip8_fx1n = [self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuFx15,
                           self.cpuNULL, self.cpuNULL, self.cpuFx18,
                           self.cpuNULL, self.cpuNULL, self.cpuNULL,
                           self.cpuNULL, self.cpuNULL, self.cpuFx1E,
                           self.cpuNULL]

    def reset(self):
        self.program_counter = 0x200 # Program starts at 0x200
        self.opcode = 0
        self.i = 0
        self.stack_pointer = 0

        self.clear_screen()

        self.stack = [0] * 16
        self.v = [0] * 16
        self.key = [0] * 16

        self.memory = [0] * 4096

        for (counter, font) in enumerate(self.fontset):
            self.memory[counter] = font

        self.delay_timer = 0
        self.sound_timer = 0

        self.test_rand = False

    def clear_screen(self):
        self.graphics = [0] * (self.screen_width * self.screen_height)
        self.draw_flag = True

    def load_game(self, game):
        print("Loading game %s" % game)
        with open(game, 'rb') as game_file:
            counter = 0
            while True:
                byte = game_file.read(1)
                if byte == '':
                    break
                self.memory[0x200 + counter] = numpy.fromstring(byte, dtype=numpy.uint8, count=1)
                counter += 1

    def emulate_cycle(self):
        self.execute_opcode()
        self.count_down_timers()

    def count_down_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("\aBeep!") # The \a produces the beep!
            self.sound_timer -= 1

    def execute_opcode(self):
        self.fetch_opcode()
        self.chip8_table[(self.opcode & 0xF000) >> 12]()

    def fetch_opcode(self):
        opcode1 = numpy.uint16(self.memory[self.program_counter])
        opcode2 = numpy.uint16(self.memory[self.program_counter + 1])
        self.opcode = opcode1 << 8 | opcode2

    def set_keys(self):
        print("Setting Keys")

    # We have a failed instruction. Skip it, move on, but echo it out to the screen.
    def cpuNULL(self):
        # We are either not implementing an opcode, or there is a programming
        # error, hopefully on the src rom, and not here.
        print("Unkown Opcode %x" % self.opcode)
        self.program_counter += 2

    def cpu0xxx(self):
        # We have a system instruction. See what the last 4 bits are for
        # instruction, ensuring that the second to last 4 bits are 0xE
        if (self.opcode & 0xFF0) >> 4 == 0xE:
            self.chip8_system[(self.opcode & 0xF)]()
        else:
            # This 'should' call a RCA 1802 program at 0NNN, but we are
            # not implementing that
            self.cpuNULL()

    # 00E0 - Clear the screen
    def cpu00E0(self):
        self.clear_screen()
        self.program_counter += 2

    # 00EE - Return from a sub routine
    def cpu00EE(self):
        self.stack_pointer -= 1
        self.program_counter = self.stack[self.stack_pointer]
        self.program_counter += 2

    # 1NNN - Jumps to Address NNN
    def cpu1xxx(self):
        self.program_counter = (self.opcode & 0xFFF)

    # 2NNN - Call subroutine at NNN
    def cpu2xxx(self):
        self.stack[self.stack_pointer] = self.program_counter
        self.stack_pointer += 1
        self.program_counter = (self.opcode & 0xFFF)

    # 3XNN - Skips next instruction if VX == NN
    def cpu3xxx(self):
        if self.v[(self.opcode & 0xF00) >> 8] == (self.opcode & 0xFF):
            self.program_counter += 4
        else:
            self.program_counter += 2

    # 4XNN - Skips next instruction if VX != NN
    def cpu4xxx(self):
        if self.v[(self.opcode & 0xF00) >> 8] != (self.opcode & 0xFF):
            self.program_counter += 4
        else:
            self.program_counter += 2

    # 5XY0 - Skips next instruction if VX == VY
    # This might possibly bug as it will accept any final 4 bit value, and not just 0
    def cpu5xxx(self):
        if self.v[(self.opcode & 0xF00) >> 8] == self.v[(self.opcode & 0xF0) >> 4]:
            self.program_counter += 4
        else:
            self.program_counter += 2

    # 6XNN - Sets VX to NN
    def cpu6xxx(self):
        self.v[(self.opcode & 0xF00) >> 8] = (self.opcode & 0xFF)
        self.program_counter += 2

    # 7XNN - Adds NN to VX
    def cpu7xxx(self):
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] + (self.opcode & 0xFF)
        # Ensure that the value is still 8bit.
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] & 0xFF
        self.program_counter += 2

    # No Instruction yet
    def cpu8xxx(self):
        # We have some CPU Arithmetic. See what the last 4 bits are for instruction
        self.chip8_arithmetic[(self.opcode & 0xF)]()

    # 8XY0 - Sets VX to the value of VY
    def cpu8xx(self):
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF0) >> 4]
        self.program_counter += 2

    # 8XY1 - Sets VX to the value of VX OR VY
    def cpu8xx1(self):
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] | self.v[(self.opcode & 0xF0) >> 4]
        self.program_counter += 2

    # 8XY2 - Sets VX to the value of VX AND VY
    def cpu8xx2(self):
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] & self.v[(self.opcode & 0xF0) >> 4]
        self.program_counter += 2

    # 8XY3 - Sets VX to the value of VX XOR VY
    def cpu8xx3(self):
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] ^ self.v[(self.opcode & 0xF0) >> 4]
        self.program_counter += 2

    # 8XY4 - Adds VY to VX. VF is set to 1 if there is a carry. Else 0
    def cpu8xx4(self):
        if self.v[(self.opcode & 0xF0) >> 4] > (0xFF - self.v[(self.opcode & 0xF00) >> 8]):
            self.v[0xF] = 0x1
        else:
            self.v[0xF] = 0x0
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] + self.v[(self.opcode & 0xF0) >> 4]
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] & 0xFF
        self.program_counter += 2

    # 8XY5 - Subtracts VY from VX. VF is set to 0 if there is a borrow. Else 1
    def cpu8xx5(self):
        if self.v[(self.opcode & 0xF00) >> 8] < self.v[(self.opcode & 0xF0) >> 4]:
            self.v[0xF] = 0x0
        else:
            self.v[0xF] = 0x1
        # For some reason,
        # self.v[(self.opcode & 0xF00) >> 8] -= self.v[(self.opcode & 0xF0) >> 4]
        # was causing V7 to be affected in addition to V0 when running 8015
        # Totally wierd bug there, but I don't think it is mine.
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] - self.v[(self.opcode & 0xF0) >> 4]
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] & 0xFF
        self.program_counter += 2

    # 8XY6 - Shifts VX right by 1. VF is set to LSB of VX before the shift.
    # Not really sure what the Y in this is for.
    def cpu8xx6(self):
        self.v[0xF] = self.v[(self.opcode & 0xF00) >> 8] & 0x1
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] >> 0x1
        self.program_counter += 2

    # 8XY7 - Sets VX to the value of VY minus VX
    def cpu8xx7(self):
        if self.v[(self.opcode & 0xF0) >> 4] < self.v[(self.opcode & 0xF00) >> 8]:
            self.v[0xF] = 0x0
        else:
            self.v[0xF] = 0x1
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF0) >> 4] - self.v[(self.opcode & 0xF00) >> 8]
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] & 0xFF
        self.program_counter += 2

    # 8XYE - Shifts VX left by 1. VF is set to MSB of VX before the shift.
    # Not really sure what the Y in this is for.
    def cpu8xxE(self):
        self.v[0xF] = self.v[(self.opcode & 0xF00) >> 8] >> 7
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] << 1
        self.v[(self.opcode & 0xF00) >> 8] = self.v[(self.opcode & 0xF00) >> 8] & 0xFF
        self.program_counter += 2

    # 9XY0 - Skips the next instruction if VX doesn't equal VY
    def cpu9xxx(self):
        if self.v[(self.opcode & 0xF00) >> 8] != self.v[(self.opcode & 0xF0) >> 4]:
            self.program_counter += 4
        else:
            self.program_counter += 2

    # ANNN - Sets I to address NNN
    def cpuAxxx(self):
        self.i = self.opcode & 0xFFF
        self.program_counter += 2

    # BNNN - Jumps to the address NNN + V0
    def cpuBxxx(self):
        self.i = (self.opcode & 0xFFF) + self.v[0x0]
        self.program_counter += 2

    # CXNN - Sets VX to a random number AND NN
    def cpuCxxx(self):
        ran = random.Random()
        if self.test_rand:
            ran.seed(123)
        self.v[(self.opcode & 0xF00) >> 8] = (self.opcode & 0xFF) & ran.randint(0x0, 0xFF)
        self.program_counter += 2

    # DXYN - Draws a sprite at coordinate XV,XY that is 8 pixels wide and N pixels tall and starting at location I
    # VF is set to one if any pixels are set from 1 to 0.
    def cpuDxxx(self):
        x = self.v[(self.opcode & 0xF00) >> 8]
        y = self.v[(self.opcode & 0xF0) >> 4]
        height = self.opcode & 0xF

        self.v[0xF] = 0
        for y_line in range(0, height):
            pixel = self.memory[self.i + y_line]
            for x_line in range(0, 8):
                if (pixel & (0x80 >> x_line)) != 0:
                    v_byte = (x + x_line + ((y + y_line) * self.screen_width))
                    # Cheap fix. v_byte should never be 2048 or above, but for some reason it is.
                    # if we skip it when this happens. we are all ok. Otherwise, crashville.
                    if v_byte < 2048:
                        if self.graphics[v_byte] == 1:
                            self.v[0xF] = 1
                        self.graphics[v_byte] ^= 1
                    else:
                        sys.exit()

        self.program_counter += 2
        self.draw_flag = True

    def cpuExxx(self):
        self.chip8_skip[(self.opcode & 0xF0) >> 4]()

    # EX9E - Skips next instruction is key stored in VX is pressed.
    # This might possibly bug as it will accept any final 4 bit value, and not just E
    def cpuEx9x(self):
        if self.key[self.v[(self.opcode & 0xF00) >> 8]] != 0x0:
            self.program_counter += 2
        self.program_counter += 2

    # EXA1 - Skips next instruction is key stored in VX isn't pressed.
    # This might possibly bug as it will accept any final 4 bit value, and not just 1
    def cpuExAx(self):
        if self.key[self.v[(self.opcode & 0xF00) >> 8]] == 0x0:
            self.program_counter += 2
        self.program_counter += 2

    def cpuFxxx(self):
        self.chip8_misc[(self.opcode & 0xF0) >> 4]()

    def cpuFxx(self):
        self.chip8_fxn[(self.opcode & 0xF)]()

    # Fx7 - Sets VX to the value of the delay timer
    def cpuFx7(self):
        self.v[(self.opcode & 0xF00) >> 8] = self.delay_timer
        self.program_counter += 2

    # FxA - A key press is awaited and stored in VX
    def cpuFxA(self):
        key_press = False
        for i in range (0, 0xF):
            if self.key[i] == 1:
                self.v[(self.opcode & 0xF00) >> 8] = i
                key_press = True
        if key_press:
            self.program_counter += 2

    def cpuFx1x(self):
        self.chip8_fx1n[(self.opcode & 0xF)]()

    # FX15 - Sets the delay timer to VX
    def cpuFx15(self):
        self.delay_timer = self.v[(self.opcode & 0xF00) >> 8]
        self.program_counter += 2

    # FX18 - Sets the sound timer to VX
    def cpuFx18(self):
        self.sound_timer = self.v[(self.opcode & 0xF00) >> 8]
        self.program_counter += 2

    # FX1E - Adds VX to I
    def cpuFx1E(self):
        if self.i + self.v[(self.opcode & 0xF00) >> 8] > 0xFFF:
            self.v[0xF] = 1
        else:
            self.v[0xF] = 0
        self.i += self.v[(self.opcode & 0xF00) >> 8]
        self.i &= 0xFFF
        self.program_counter += 2

    # FX29 - Sets I to the location of the sprite for the character in VX
    # This might possibly bug as it will accept any final 4 bit value, and not just 9
    # I took this from another example. I will come back to look at it later
    def cpuFx2x(self):
        self.i = self.v[(self.opcode & 0xF00) >> 8] * 0x5
        self.program_counter += 2

    # FX33 - Stores the BCD representation of VX at I, I+1 and I+2
    # This might possibly bug as it will accept any final 4 bit value, and not just 3
    # Taken from elsewhere
    def cpuFx3x(self):
        self.memory[self.i] = self.v[(self.opcode & 0xF00) >> 8] / 100
        self.memory[self.i + 1] = (self.v[(self.opcode & 0xF00) >> 8] / 10) % 10
        self.memory[self.i + 2] = (self.v[(self.opcode & 0xF00) >> 8] % 100) % 10
        self.program_counter += 2

    # FX55 - Stores V0 to VX in memory starting at address I
    # This might possibly bug as it will accept any final 4 bit value, and not just 5
    def cpuFx5x(self):
        for counter in range(0, ((self.opcode & 0xF00) >> 8) + 1):
            self.memory[self.i + counter] = self.v[counter]
        self.i = self.i + (self.opcode & 0xF00 >> 8) + 1
        self.program_counter += 2

    # FX65 - Fills V0 to VX with values from memory starting at address I
    # This might possibly bug as it will accept any final 4 bit value, and not just 5
    def cpuFx6x(self):
        for counter in range(0, ((self.opcode & 0xF00) >> 8) + 1):
            self.v[counter] = self.memory[self.i + counter]
        self.i = self.i + (self.opcode & 0xF00 >> 8) + 1
        self.program_counter += 2
