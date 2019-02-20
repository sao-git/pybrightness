#!/usr/bin/env python
from sys import argv, exit, stderr
from typing import TextIO, Tuple

# See https://wiki.archlinux.org/index.php/Backlight#ACPI for more information
# on the method used in this script.
#
# TODO:
#    * Have the user set the backlight path and files in a config file
#    * Maybe use an exponential curve instead of a power curve
#    * Explore increasing MAX effectively and/or accepting real inputs


# File to write new brightness, can also be read to get current value
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


if __name__ == "__main__":
    # Base path to required "files"
    path = "/sys/class/backlight/intel_backlight"
    # Maximum output brightness as an integer
    get_this = "/max_brightness"
    set_this = "/brightness"

    check_this = "/actual_brightness"


    if len(argv) == 1:
        actual_brightness: int = read_val(path + check_this)

        print(actual_brightness)
        exit(0)


    # Grab the maximum brightness value
    max_brightness: int = read_val(path + get_this)

    # Take the first argument on the command line as integer input.
    arg = int(argv[1])

    # Since output must be rounded, the MAX must be low enough to make lower
    # input values effective, i.e. setting MAX too high will cause lower inputs to
    # round to MIN.
    MAX = 25
    # Minimum input as well as minimum output, since setting to 0 will turn the
    # display off. There is typically a better way to do that.
    MIN = 5

    if arg < MIN:
        arg = MIN
    elif arg > MAX:
        arg = MAX

    # Exponent that scales the input to output curve. A positive exponent devotes
    # more of the input values to lower brightness levels.
    exponent = 3

    # The input to output curve.
    val: int = round(MIN + (arg / MAX)**exponent * (max_brightness - MIN))

    # Write out the brightness level and exit with a success code.
    len_val, len_written = set_val(path + set_this, val)

    if len_val == len_written:
        exit(0)
    else:
        print("something went wrong", file=stderr)
        exit(1)
