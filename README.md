# pybrightness

A Python script to change screen brightness via the [ACPI method](https://wiki.archlinux.org/index.php/Backlight#ACPI) on Linux. Written because other methods either failed (`xbacklight`) or required heavy dependencies (`gnome`).

In order to use this script, you must have read and write permissions on the relevant files in `/sys/class/backlight/{KERNEL}`. From the above wiki page:

`/etc/udev/rules.d/backlight.rules`
```
ACTION=="add", SUBSYSTEM=="backlight", KERNEL=="intel_backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness"
ACTION=="add", SUBSYSTEM=="backlight", KERNEL=="intel_backlight", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"
```

The current version requires setting the files within the script. A future version will have a small configuration file for separation of code and data. The code should be simple enough to work on all Python versions without dependencies.

Released to the public domain.
