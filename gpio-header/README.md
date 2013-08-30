gpio-header
==========

Generates device tree overlays for easy gpio mux control.

#### Usage

##### Generate and install the overlay files (optional)

Or, if you're lazy/don't have python, grab the files from the "generated" directory.

Generate the dts files, the compile script, and the install script with

    python generateGPIOOverlays.py
    
On the beaglebone, compile the .dts files to .dtbo

    sh compile.sh
    
Copy the generated .dtbo files to /lib/firmware (or copy manually):

    sh install.sh
    
##### Use the overlay

Setup P9.11 mux for gpio

    echo gpio-P9.11 > /sys/devices/bone_capemgr.*/slots
    
Set the mux values to rx-enable (input) with the pull-up (100uA):

    echo rxEnable_pullUp >/sys/devices/ocp*/gpio_P9.11_helper*/state
    
Now disable the pullup:

    echo rxEnable_pullNone >/sys/devices/ocp*/gpio_P9.11_helper*/state
    
###### Valid States

    rxDisable_pullNone
    rxEnable_pullNone
    rxDisable_pullUp
    rxEnable_pullUp
    rxDisable_pullDown
    rxEnable_pullDown
