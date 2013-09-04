led-header
==========

Generates device tree overlays for easy gpio led control.

#### Usage

##### Generate and install the overlay files (optional)

Or, if you're lazy/don't have python, grab the files from the "generated" directory.

Generate the dts files, the compile script, and the install script with

    python generateLEDOverlays.py
    
On the beaglebone, compile the .dts files to .dtbo

    sh compile.sh
    
Copy the generated .dtbo files to /lib/firmware (or copy manually):

    sh install.sh
    
##### Use the overlay

Setup P9.11 for use as a gpio-led

    echo led-P9.11 > /sys/devices/bone_capemgr.*/slots
    
Set the led to blink according to cpu usage.
    
    echo cpu0 > trigger /sys/class/leds/leds:P9.11/trigger

