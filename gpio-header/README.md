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

Setup P9.11 mux for gpio (do "ls /lib/firmware/gpio*P9.11*" to find the proper gpio index).
**NOTE: I don't neccesarily like this naming since it requires finding something. An alternative would be to keep the naming without the gpio index (so, gpio-p9.11), and change the ocp interface name from "gpio_P9.11_helper" to "gpio_P9.11_gpio28". Then, to find the gpio index for that header, you could just "ls /sys/devices/ocp*/gpio_P9.11_*". That would at least make grepping a little easier.
Open to suggestions. Either way, you have to find the index so it can be exported. **

    echo gpio28-P9.11 > /sys/devices/bone_capemgr.*/slots
    
Set the mux values to rx-enable (input) with the pull-up (100uA):

    echo rxEnable_pullUp >/sys/devices/ocp*/gpio_P9.11_helper*/state
    
Now disable the pullup:

    echo rxEnable_pullNone >/sys/devices/ocp*/gpio_P9.11_helper*/state
    
Now export the gpio pin so we can use it. Use the index shown in the file.

    eho 28 > /sys/class/gpio/export

Now set the gpio to high:

    echo 0 > /sys/class/gpio/gpio28/value

    
###### Valid States

    rxDisable_pullNone
    rxEnable_pullNone
    rxDisable_pullUp
    rxEnable_pullUp
    rxDisable_pullDown
    rxEnable_pullDown
