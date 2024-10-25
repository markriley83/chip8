#!/bin/env python
#####
#
# Chip 8 emulator
#
# pretty much copied from http://www.multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
#
#####
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import time
import chip8

window_name = 'Chip8 Emulator'
screen_width = 64
screen_height = 32
modifier = 10
display_width = screen_width * modifier
display_height = screen_height * modifier
screen_data = [[[0]*3]*screen_width]*screen_height

def main():
    global my_chip8

    if not sys.argv[1]:
        print("You must specify game to load")

    my_chip8 = chip8.Chip8()
    my_chip8.initialise()
    my_chip8.load_game(sys.argv[1])

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(display_width, display_height)
    glutCreateWindow(window_name)

    glutDisplayFunc(display)

    glutIdleFunc(display)
    glutReshapeFunc(reshape_window)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)

    glutMainLoop()

def update_screen():
    for y in range(0, my_chip8.screen_height):
        for x in range(0, my_chip8.screen_width):
            if my_chip8.graphics[(y * my_chip8.screen_width) + x] == 1:
                glColor3f(1.0,1.0,1.0);
                glBegin(GL_QUADS);
                glVertex3f((x * modifier) + 0.0,      (y * modifier) + 0.0, 0.0);
                glVertex3f((x * modifier) + 0.0,      (y * modifier) + modifier, 0.0);
                glVertex3f((x * modifier) + modifier, (y * modifier) + modifier, 0.0);
                glVertex3f((x * modifier) + modifier, (y * modifier) + 0.0, 0.0);
                glEnd();

def display():
    start = time.clock() # get current time for timing purposes.
    # emulate chip 8 cycle
    my_chip8.emulate_cycle()
    if my_chip8.draw_flag:
        glClear(GL_COLOR_BUFFER_BIT)
        update_screen()
        glutSwapBuffers()
        my_chip8.draw_flag = False
    if (1.0 / my_chip8.ops_per_second - (time.clock() - start)) > 0:
        time.sleep(1.0 / my_chip8.ops_per_second - (time.clock() - start)) # We sleep a bit to keep timing right

def reshape_window(w, h):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, h, 0)
    glMatrixMode(GL_MODELVIEW)
    glViewport(0, 0, w, h)

    # Resize quad
    display_width = w
    display_height = h

def keyboard_down(key, x, y):
    if key == '\033': # esc
        sys.exit()

    if key == '1':
        my_chip8.key[0x1] = 1
    elif key == '2':
        my_chip8.key[0x2] = 1
    elif key == '3':
        my_chip8.key[0x3] = 1
    elif key == '4':
        my_chip8.key[0xC] = 1

    elif key == 'q':
        my_chip8.key[0x4] = 1
    elif key == 'w':
        my_chip8.key[0x5] = 1
    elif key == 'e':
        my_chip8.key[0x6] = 1
    elif key == 'r':
        my_chip8.key[0xD] = 1

    elif key == 'a':
        my_chip8.key[0x7] = 1
    elif key == 's':
        my_chip8.key[0x8] = 1
    elif key == 'd':
        my_chip8.key[0x9] = 1
    elif key == 'f':
        my_chip8.key[0xE] = 1

    elif key == 'z':
        my_chip8.key[0xA] = 1
    elif key == 'x':
        my_chip8.key[0x0] = 1
    elif key == 'c':
        my_chip8.key[0xB] = 1
    elif key == 'v':
        my_chip8.key[0xF] = 1

def keyboard_up(key, x, y):
    if key == '1':
        my_chip8.key[0x1] = 0
    elif key == '2':
        my_chip8.key[0x2] = 0
    elif key == '3':
        my_chip8.key[0x3] = 0
    elif key == '4':
        my_chip8.key[0xC] = 0

    elif key == 'q':
        my_chip8.key[0x4] = 0
    elif key == 'w':
        my_chip8.key[0x5] = 0
    elif key == 'e':
        my_chip8.key[0x6] = 0
    elif key == 'r':
        my_chip8.key[0xD] = 0

    elif key == 'a':
        my_chip8.key[0x7] = 0
    elif key == 's':
        my_chip8.key[0x8] = 0
    elif key == 'd':
        my_chip8.key[0x9] = 0
    elif key == 'f':
        my_chip8.key[0xE] = 0

    elif key == 'z':
        my_chip8.key[0xA] = 0
    elif key == 'x':
        my_chip8.key[0x0] = 0
    elif key == 'c':
        my_chip8.key[0xB] = 0
    elif key == 'v':
        my_chip8.key[0xF] = 0

if __name__ == '__main__':
    main()
