#!/usr/bin/python3

# WordClock

import sys, os, time, argparse, atexit, signal
from datetime import datetime
from string import digits

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import numpy as np

# Constants
MATRIX_W      = 32 # Number of Actual X Pixels
MATRIX_H      = 32 # Number of Actual Y Pixels
MATRIX_DEPTH  = 3  # Color Depth (RGB=3)
MATRIX_DIV    = 2  # Physical Matrix is Half of Pixel Matrix

# Colors
RED     = [255, 0,   0  ]
LIME    = [0,   255, 0  ]
BLUE    = [0,   0,   255]
YELLOW  = [255, 255, 0  ]
FUCHSIA = [255, 0,   255]
AQUA    = [0,   255, 255]
WHITE   = [255, 255, 255]

# Birthday
BIRTH_MONTH = 2
BIRTH_DAY = 2


# Enumerate RGB Matrix Object
options = RGBMatrixOptions()
options.rows = MATRIX_H
options.cols = MATRIX_W
options.pwm_bits = 8 
options.limit_refresh_rate_hz = 100 
options.gpio_slowdown = 3 
options.hardware_mapping = 'adafruit-hat' 

matrix = RGBMatrix(options = options)

# Word Dictionary
# Uses the Physical Grid mapping for the cut 16x16 grid:
# X is 1 - 16 inclusive
# Y is 1 - 16 includive
# Origin is top left corner 
m = {
    "hello"     : {"row" : 1,  "start" : 1,  "length" : 5, "height" : 1},
    "happy"     : {"row" : 1,  "start" : 6,  "length" : 5, "height" : 1},
    "new"       : {"row" : 1,  "start" : 12, "length" : 3, "height" : 1},
    "snowflake" : {"row" : 1,  "start" : 16, "length" : 1, "height" : 1},
    "it"        : {"row" : 2,  "start" : 1,  "length" : 2, "height" : 1},
    "is"        : {"row" : 2,  "start" : 4,  "length" : 2, "height" : 1},
    "twenty"    : {"row" : 2,  "start" : 7,  "length" : 6, "height" : 1},
    "year!"     : {"row" : 2,  "start" : 12, "length" : 5, "height" : 1},
    "two1"      : {"row" : 3,  "start" : 1,  "length" : 3, "height" : 1},
    "one1"      : {"row" : 3,  "start" : 3,  "length" : 3, "height" : 1},
    "eleven1"   : {"row" : 3,  "start" : 5,  "length" : 6, "height" : 1},
    "twelve1"   : {"row" : 3,  "start" : 11, "length" : 6, "height" : 1},
    "six1"      : {"row" : 4,  "start" : 1,  "length" : 3, "height" : 1},
    "sixteen"   : {"row" : 4,  "start" : 1,  "length" : 7, "height" : 1},
    "three1"    : {"row" : 4,  "start" : 8,  "length" : 5, "height" : 1},
    "five1"     : {"row" : 4,  "start" : 13, "length" : 4, "height" : 1},
    "ten1"      : {"row" : 2,  "start" : 7,  "length" : 1, "height" : 3},
    "eddie"     : {"row" : 5,  "start" : 1,  "length" : 5, "height" : 1},
    "quarter"   : {"row" : 5,  "start" : 6,  "length" : 7, "height" : 1},
    "half"      : {"row" : 5,  "start" : 13, "length" : 4, "height" : 1},
    "seven1"    : {"row" : 6,  "start" : 1,  "length" : 5, "height" : 1},
    "seventeen" : {"row" : 6,  "start" : 1,  "length" : 9, "height" : 1},
    "nine1"     : {"row" : 6,  "start" : 9,  "length" : 4, "height" : 1},
    "nineteen"  : {"row" : 6,  "start" : 9,  "length" : 8, "height" : 1},
    "thirteen"  : {"row" : 7,  "start" : 1,  "length" : 8, "height" : 1},
    "eight1"    : {"row" : 7,  "start" : 9,  "length" : 5, "height" : 1},
    "eighteen"  : {"row" : 7,  "start" : 9,  "length" : 8, "height" : 1},
    "four1"     : {"row" : 8,  "start" : 1,  "length" : 4, "height" : 1},
    "fourteen"  : {"row" : 8,  "start" : 1,  "length" : 8, "height" : 1},
    "minutes"   : {"row" : 8,  "start" : 10, "length" : 7, "height" : 1},
    "minute"    : {"row" : 8,  "start" : 10, "length" : 6, "height" : 1},
    "past"      : {"row" : 9,  "start" : 1,  "length" : 4, "height" : 1},
    "to"        : {"row" : 9,  "start" : 4,  "length" : 2, "height" : 1},
    "heart"     : {"row" : 9,  "start" : 6,  "length" : 1, "height" : 1},
    "two2"      : {"row" : 9,  "start" : 7,  "length" : 3, "height" : 1},
    "one2"      : {"row" : 9,  "start" : 9,  "length" : 3, "height" : 1},
    "three2"    : {"row" : 9,  "start" : 12, "length" : 5, "height" : 1},
    "twelve2"   : {"row" : 10, "start" : 1,  "length" : 6, "height" : 1},
    "seven2"    : {"row" : 10, "start" : 8,  "length" : 5, "height" : 1},
    "nine2"     : {"row" : 10, "start" : 13, "length" : 4, "height" : 1},
    "five2"     : {"row" : 11, "start" : 1,  "length" : 4, "height" : 1},
    "six2"      : {"row" : 11, "start" : 5,  "length" : 3, "height" : 1},
    "eleven2"   : {"row" : 11, "start" : 8,  "length" : 6, "height" : 1},
    "ten2"      : {"row" : 11, "start" : 14, "length" : 3, "height" : 1},
    "eight2"    : {"row" : 12, "start" : 1,  "length" : 5, "height" : 1},
    "four2"     : {"row" : 12, "start" : 6,  "length" : 4, "height" : 1},
    "oclock"    : {"row" : 12, "start" : 11, "length" : 6, "height" : 1},
    "in"        : {"row" : 13, "start" : 1,  "length" : 2, "height" : 1},
    "the"       : {"row" : 13, "start" : 4,  "length" : 3, "height" : 1},
    "afternoon" : {"row" : 13, "start" : 8,  "length" : 9, "height" : 1},
    "noon"      : {"row" : 13, "start" : 13, "length" : 4, "height" : 1},
    "christmas" : {"row" : 14, "start" : 1,  "length" : 9, "height" : 1},
    "morning"   : {"row" : 14, "start" : 10, "length" : 7, "height" : 1},
    "evening"   : {"row" : 15, "start" : 1,  "length" : 7, "height" : 1},
    "birthday!" : {"row" : 15, "start" : 8,  "length" : 9, "height" : 1},
    "have"      : {"row" : 16, "start" : 1,  "length" : 4, "height" : 1},
    "a"         : {"row" : 16, "start" : 6,  "length" : 1, "height" : 1},
    "nice"      : {"row" : 16, "start" : 8,  "length" : 4, "height" : 1},
    "day!"      : {"row" : 16, "start" : 13, "length" : 4, "height" : 1}
}

# Generates the Appropriate Word List, given a datetime object. Defaults to Current Time
def getTimeWords(t=None):
    if t is None:
        t= datetime.now()
    words = ['hello']

    if  t.hour != 12:
        words += ['oclock']
    
    # Minutes/OClock
    words += ['it','is']
    if t.minute == 1:
        words += ['one1','minute','past']
    elif t.minute == 2:
        words += ['two1','minutes','past']
    elif t.minute == 3:
        words += ['three1','minutes','past']
    elif t.minute == 4:
        words += ['four1','minutes','past']
    elif t.minute == 5:
        words += ['five1','minutes','past']
    elif t.minute == 6:
        words += ['six1','minutes','past']
    elif t.minute == 7:
        words += ['seven1','minutes','past']
    elif t.minute == 8:
        words += ['eight1','minutes','past']
    elif t.minute == 9:
        words += ['nine1','minutes','past']
    elif t.minute == 10:
        words += ['ten1','minutes','past']
    elif t.minute == 11:
        words += ['eleven1','minutes','past']
    elif t.minute == 12:
        words += ['twelve1','minutes','past']
    elif t.minute == 13:
        words += ['thirteen','minutes','past']
    elif t.minute == 14:
        words += ['fourteen','minutes','past']
    elif t.minute ==15:
        words += ['quarter','past']
    elif t.minute == 16:
        words += ['sixteen','minutes','past']
    elif t.minute == 17:
        words += ['seventeen','minutes','past']
    elif t.minute == 18:
        words += ['eighteen','minutes','past']
    elif t.minute == 19:
        words += ['nineteen','minutes','past']
    elif t.minute == 20:
        words += ['twenty','minutes','past']
    elif t.minute == 21:
        words += ['twenty','one1','minutes','past']
    elif t.minute == 22:
        words += ['twenty','two1','minutes','past']
    elif t.minute == 23:
        words += ['twenty','three1','minutes','past']
    elif t.minute == 24:
        words += ['twenty','four1','minutes','past']
    elif t.minute == 25:
        words += ['twenty','five1','minutes','past']
    elif t.minute == 26:
        words += ['twenty','six1','minutes','past']
    elif t.minute == 27:
        words += ['twenty','seven1','minutes','past']
    elif t.minute == 28:
        words += ['twenty','eight1','minutes','past']
    elif t.minute == 29:
        words += ['twenty','nine1','minutes','past']
    elif t.minute == 30:
        words += ['half','past']
    elif t.minute == 31:
        words += ['twenty','nine1','minutes','to'] 
    elif t.minute == 32:
        words += ['twenty','eight1','minutes','to']
    elif t.minute == 33:
        words += ['twenty','seven1','minutes','to']
    elif t.minute == 34:
        words += ['twenty','six1','minutes','to']
    elif t.minute == 35:
        words += ['twenty','five1','minutes','to']
    elif t.minute == 36:
        words += ['twenty','four1','minutes','to']
    elif t.minute == 37:
        words += ['twenty','three1','minutes','to']
    elif t.minute == 38:
        words += ['twenty','two1','minutes','to']
    elif t.minute == 39:
        words += ['twenty','one1','minutes','to']
    elif t.minute == 40:
        words += ['twenty','minutes','to']
    elif t.minute == 41:
        words += ['nineteen','minutes','to']
    elif t.minute == 42:
        words += ['eighteen','minutes','to']
    elif t.minute == 43:
        words += ['seventeen','minutes','to']
    elif t.minute == 44:
        words += ['sixteen','minutes','to']
    elif t.minute == 45:
        words += ['quarter','to']
    elif t.minute == 46:
        words += ['fourteen','minutes','to']
    elif t.minute == 47:
        words += ['thirteen','minutes','to']
    elif t.minute == 48:
        words += ['twelve1','minutes','to']
    elif t.minute == 49:
        words += ['eleven1','minutes','to']
    elif t.minute == 50:
        words += ['ten1','minutes','to']
    elif t.minute == 51:
        words += ['nine1','minutes','to']
    elif t.minute == 52:
        words += ['eight1','minutes','to']
    elif t.minute == 53:
        words += ['seven1','minutes','to']
    elif t.minute == 54:
        words += ['six1','minutes','to']
    elif t.minute == 55:
        words += ['five1','minutes','to']
    elif t.minute == 56:
        words += ['four1','minutes','to']
    elif t.minute == 57:
        words += ['three1','minutes','to']
    elif t.minute == 58:
        words += ['two1','minutes','to']
    elif t.minute == 59:
        words += ['one1','minute','to']
    
    
    # Hours
    if t.minute > 30:
        disp_hour = t.hour + 1
    else:
        disp_hour = t.hour

    if disp_hour == 0 or disp_hour == 24:
        words += ['twelve2']
    elif disp_hour == 12:
        words += ['noon']
    elif disp_hour == 1 or disp_hour == 13:
        words += ['one2']
    elif disp_hour == 2 or disp_hour == 14:
        words += ['two2']
    elif disp_hour == 3 or disp_hour == 15:
        words += ['three2']
    elif disp_hour == 4 or disp_hour == 16:
        words += ['four2']
    elif disp_hour == 5 or disp_hour == 17:
        words += ['five2']
    elif disp_hour == 6 or disp_hour == 18:
        words += ['six2']
    elif disp_hour == 7 or disp_hour == 19:
        words += ['seven2']
    elif disp_hour == 8 or disp_hour == 20:
        words += ['eight2']
    elif disp_hour == 9 or disp_hour == 21:
        words += ['nine2']
    elif disp_hour == 10 or disp_hour == 22:
        words += ['ten2']
    elif disp_hour == 11 or disp_hour == 23:
        words += ['eleven2']

    # Time of Day
    if t.hour >= 0 and t.hour < 12:
        words += ['in','the','morning']
    elif t.hour > 12 and t.hour < 17:
        words += ['in','the','afternoon']
    elif t.hour >= 17 and t.hour <= 24:
        words += ['in','the','evening']

    translation = str.maketrans("", "", digits)   
    print(t.strftime('%I:%M:%S %p') + " - " + (' '.join(words)).translate(translation))

    return words

# Generate the Pixel Buffer based on what words should be illuminated
# primary_words: The list of words to light up in the primary_color (usually the time)
# secondary_words: The list of words to light up in the secondary color (usually a special message)
# fade_steps_time is the added delay time between each of the fade steps (float, seconds)
# fade_steps_number is the number of intermediate colors in the fade
start_buff = np.zeros((MATRIX_H * MATRIX_DIV, MATRIX_W * MATRIX_DIV, 3), dtype=np.int16)
def setDisplay(primary_words=[], primary_color=RED, secondary_words=[], secondary_color=AQUA, tertiary_words=[], tertiary_color = WHITE, fade_steps_time=0, fade_steps_number=20):
    global start_buff

    end_buff = np.zeros((MATRIX_H * MATRIX_DIV, MATRIX_W * MATRIX_DIV, 3), dtype=np.int16)

    for word in primary_words + secondary_words + tertiary_words:
        pixel_x = (m[word]["start"]-1) * MATRIX_DIV
        pixel_y = (m[word]["row"] - 1) * MATRIX_DIV
        for y_adder in range(m[word]["height"]*MATRIX_DIV):
            for x_adder in range(m[word]["length"]*MATRIX_DIV):
                if word in primary_words:
                    color = primary_color
                elif word in secondary_words:
                    color = secondary_color
                elif word in tertiary_words:
                    color = tertiary_color
                end_buff[pixel_y+y_adder][pixel_x + x_adder] = color

    # Fade between buffers
    diff_buff = end_buff - start_buff
    frame_add = diff_buff/fade_steps_number
    frame = start_buff
    for f in range(fade_steps_number):
        frame = frame + frame_add
        matrix.SetImage(Image.fromarray(frame.astype('uint8'), 'RGB'))
        time.sleep(fade_steps_time)

    start_buff = end_buff # Use this global var for enabling state fades

# Runs the Word Clock in a certain mode
# mode (pick one):
#   basic_test: Just lights up all the word units in all the colors to test them
#   time_test: Runs through a full day at high speed in the primry color
#   clock: Normal Clock mode. Endless Loop. Can Have modifiers applied. Shows time in primary color
# primary_color: RGB primary color to use for clock words
# secondary_color: RGB color to use for modifiers


def run(mode="clock", primary_color=RED, secondary_color=AQUA, modifiers=[]):
    if mode == "basic_test":
        print("Testing each word & Color...")
        for key in m.keys():
            print("  %s" % (key))
            setDisplay([key], RED)
            time.sleep(0.2)
            setDisplay([key], LIME)
            time.sleep(0.2)
            setDisplay([key], BLUE)
            time.sleep(0.2)
        matrix.Clear()
        print("Done.")
    elif mode == "time_test":
        print("Testing All Times...")
        for hour in range(24):
            for minute in range(60):
                setDisplay(getTimeWords(datetime(2020, 1, 1, hour, minute, 0)),primary_color)
                time.sleep(0.2)
        matrix.Clear()
        print("Done.")
    elif mode == "clock":
        print("Running the Clock.")
        fade_counter = 0
        secondary_counter = 90
        while True:
            t = datetime.now()
            primary_words   = getTimeWords(t)
            secondary_words = []
            tertiary_words  = []
            tertiary_color  = []
            if "birthday" in modifiers and t.month == BIRTH_MONTH and t.day == BIRTH_DAY and secondary_counter%5 == 0 and secondary_counter < 100:
                secondary_words += ['happy','birthday']
                print("            - Happy Birthday")

            setDisplay(primary_words,primary_color,secondary_words,secondary_color,tertiary_words,tertiary_color)
            fade_counter += 1
            if fade_counter > 5:
                fade_counter = 0
            secondary_counter += 1
            if secondary_counter > 105:
                secondary_counter = 0

            time.sleep(5)
    else:
        print("Uknown mode.")  

def exit_handler():
    print('Script Aborted. Turning off Clock.')
    matrix.Clear()

#Main Execution
if __name__ == '__main__':
    atexit.register(exit_handler)
    signal.signal(signal.SIGINT, lambda x,y: sys.exit(0))
    run("clock", modifiers=["birthday"])
