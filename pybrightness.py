#!/usr/bin/env python
from sys import argv, exit, stderr
from typing import Callable, Iterable, TextIO, Tuple, Optional
from itertools import islice

# See https://wiki.archlinux.org/index.php/Backlight#ACPI for more information
# on the method used in this script.
#
# TODO:
#    * Have the user set the backlight path and files in a config file
#    * Maybe use an exponential curve instead of a power curve
#    * Explore increasing MAX effectively and/or accepting real inputs
#    * Improve the curve so that lower values don't collide (linear ramp?)


# `set_this`: file to write new brightness, can also be read to get current value
# User must have write access to this file, typically by setting a udev rule
# to give the `video` group write access and adding the user to that group:
#
# ```
# File: /etc/udev/rules.d/backlight.rules
#
# ACTION=="add", SUBSYSTEM=="backlight", KERNEL=="intel_backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness"
# ACTION=="add", SUBSYSTEM=="backlight", KERNEL=="intel_backlight", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"
# ```

def read_val(file_path: str) -> int:
    f: TextIO = open(file_path, "r")
    val = int(f.read())
    f.close()

    return val


def set_val(file_path: str, val: int) -> Tuple[int, int]:
    val_out = str(val) + '\n'

    f: TextIO = open(file_path, 'w')
    bytes_written = f.write(val_out)
    f.close()

    return len(val_out), bytes_written


def as_percent(x: int) -> str:
    return f'{x * 100:.1f}%'


def get_val_list(vals: Iterable, per_line: int, max_brightness: int) -> str:
    vals_slice = tuple(islice(vals, per_line))
    vals_out = []

    fmt = lambda i, x: f'{i} -> {x} ({as_percent(x/max_brightness)})'

    while vals_slice:
        vals_out.append(", ".join(fmt(i,x) for i,x in vals_slice))
        vals_slice = tuple(islice(vals, per_line))

    return ",\n".join(vals_out) + '\n\n'


if __name__ == "__main__":
    # Base path to required "files"
    path = "/sys/class/backlight/intel_backlight"
    # Maximum output brightness as an integer
    get_this = "/max_brightness"
    set_this = "/brightness"

    check_this = "/actual_brightness"




    # Since output must be rounded, the MAX must be low enough to make lower
    # input values effective, i.e. setting MAX too high will cause lower inputs to
    # round to MIN.
    MAX = 25
    # Minimum input as well as minimum output, since setting to 0 will turn the
    # display off. There is typically a better way to do that.
    MIN = 5


    # Exponent that scales the input to output curve. A positive exponent devotes
    # more of the input values to lower brightness levels.
    exponent = 3

    # Grab the maximum brightness value
    max_brightness: int = read_val(path + get_this)

    calc_val: Callable
    calc_val = lambda x: round(MIN + (x / MAX)**exponent * (max_brightness - MIN))

    if len(argv) == 1:
        act_val = read_val(path + check_this)
        k = (act_val - MIN)/(max_brightness - MIN)
        arg_val = round(MAX * k**(1/exponent))

        output_range: Iterable = ((i, calc_val(i)) for i in range(MIN, MAX+1))
        out1: str = get_val_list(output_range, 3, max_brightness)

        #print('Input range is [5..25]\n')
        print('Input -> Output (Percent of full brightness):\n')




        out2 = f'Current brightness is {act_val:d} out of {max_brightness}\n'
        out3 = f'Give me a value of {arg_val} to set this brightness'

        print(out1 + out2 + out3)
        exit(0)

    # Take the first argument on the command line as integer input.
    arg = int(argv[1])

    if arg < MIN:
        arg = MIN
    elif arg > MAX:
        arg = MAX

    # The input to output curve.
    val: int = calc_val(arg)

    # Write out the brightness level and exit with a success code.
    len_val, len_written = set_val(path + set_this, val)

    if len_val == len_written:
        print(f'Setting the brightness to {val:d} out of {max_brightness:d}')
        exit(0)
    else:
        print('something went wrong', file=stderr)
        exit(1)
