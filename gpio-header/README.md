Note: This is somewhat obsolete by https://github.com/cdsteinkuehler/beaglebone-universal-io

gpio-header
==========

Generates device tree overlays for easy gpio mux control.

Note, when messing with device tree overlays, you may have to reboot for any changes in the compiled blobs to take effect. The kernel firmware loader caches the blobs, and there's currently no way to flush the cache (LOL).

#### What about gpio-helper

These files have runtime configuration changes in mind. The gpio-helper exports the gpio sysfs entries to /sys/class/gpio, but once they're exported, you can't do change the direction or anything else. With the instant gratification of runtime configuration in mind, you have to export the gpio entries yourself. The setupGPIO scripts will do this for you.

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

Setup P9.11 mux for gpio:

    echo gpio-P9.11 > /sys/devices/bone_capemgr.*/slots
    
Set the mux values to rx-enable (input) with the pull-up (100uA):

    echo rxEnable_pullUp >/sys/devices/ocp*/gpio-P9.11_*/state
    
Now disable the pullup for fun:

    echo rxEnable_pullNone >/sys/devices/ocp*/gpio-P9.11_*/state
    
Now export the gpio pin so we can use it. To find the index:

    # ls -d /sys/devices/ocp*/gpio-P9.11_*
    /sys/devices/ocp.2/gpio-P9.11_gpio30.10
    
At the end, you'll see gpio30. Export gpio 30 for the gpio sysfs interface (if you want to use it):

    echo 30 > /sys/class/gpio/export

Now set the gpio to high:

    echo 1 > /sys/class/gpio/gpio30/value

    
###### Valid States

    rxDisable_pullNone
    rxEnable_pullNone
    rxDisable_pullUp
    rxEnable_pullUp
    rxDisable_pullDown
    rxEnable_pullDown
    
###### Errors
If you get an error at

    echo gpio-P9.11 > /sys/devices/bone_capemgr.*/slots
    
use the dmesg (or dmesg | tail) command to see why the overlay couldn't load (most likely a pin conflict).
