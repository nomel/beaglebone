gpio-header
==========

Generates device tree overlays for easy pru gpio mux control.

Note, when messing with device tree overlays, you may have to reboot for any changes in the compiled blobs to take effect. The kernel firmware loader caches the blobs, and there's currently no way to flush the cache (LOL).

#### What about static device tree?

These files have runtime configuration changes in mind to make quick changes easier while you're developing your code in case you want to quickly and easily change your pru gpio muxing. Since all pru header pins are included, they can be used as a reference for your own device tree overlay.

#### Usage

##### Generate and install the overlay files (optional)

Or, if you're lazy/don't have python, grab the files from the "generated" directory and run install.sh.

Generate the dts files, the compile script, and the install script with

    python generatePRUGPIOOverlays.py
    
On the beaglebone, compile the .dts files to .dtbo

    sh compile.sh
    
Copy the generated .dtbo files to /lib/firmware (or copy manually):

    sh install.sh
    
##### Use the overlay

Setup P8.30 mux (pru gpio 11). Default is input with no-pullup (first entry in overlay).

    echo prugpio-P8.29 > /sys/devices/bone_capemgr.*/slots

Set the to output:

    echo output > /sys/devices/ocp*/prugpio-P8.29_*/state
    
Set to input with pullup:

    echo input_pullUp >/sys/devices/ocp*/gpio-P9.11_*/state
    
Disable the pullup::    

    echo input_pullNone >/sys/devices/ocp*/gpio-P9.11_*/state
    
###### Valid States

    input_pullNone (default)
    input_pullDown
    input_pullUp
    output
    
###### Errors
If you get an error at

    echo prugpio-P8.29 > /sys/devices/bone_capemgr.*/slots
    
use the dmesg (or dmesg | tail) command to see why the overlay couldn't load (most likely a pin conflict, meaning something else is using that pin already).
