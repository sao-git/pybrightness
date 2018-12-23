#!/usr/bin/env python
from sys import argv, exit

# See https://wiki.archlinux.org/index.php/Backlight#ACPI for more information
# on the method used in this script.
#
# All code here *should* be compatible with all typical Python versions.
#
# TODO:
#    * Have the user set the backlight path and files in a config file
#    * Maybe use an exponential curve instead of a power curve
#    * Explore increasing MAX effectively and/or accepting real inputs

# Base path to required "files"
path = "/sys/class/backlight/intel_backlight"
# Maximum output brightness as an integer
get_this = "/max_brightness"

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
set_this = "/brightness"

# Grab the maximum brightness value
f = open(path + get_this, "r")
max_brightness = int(f.read())
f.close()

# Take the first argument on the command line as integer input.
arg = int(argv[1])

# Since output must be rounded, the MAX must be low enough to make lower
# input values effective, i.e. setting MAX too high will cause lower inputs to
# round to MIN.
MAX = 20
# Minimum input as well as minimum output, since setting to 0 will turn the
# display off. There is typically a better way to do that.
MIN = 1

if arg < MIN:
    arg = MIN
elif arg > MAX:
    arg = MAX

# Exponent that scales the input to output curve. A positive exponent devotes
# more of the input values to lower brightness levels.
exponent = 3

# The input to output curve.
val = round(MIN + (arg / MAX)**exponent * (max_brightness - MIN))

# Write out the brightness level and exit with a success code.
f = open(path + set_this, "w")
f.write(str(val) + "\n")
f.close()

exit(0)
