PRU Debug Scripts
==========

Random debug scripts that use the horribly slow devmem2 program to read/modify pru memory.

###### Scripts

Scripts for the individual prus can be found in [pru0](pru0) and [pru1](pru1).

* reset - resets the pru.
* enable - enables execution of the current firmware.
* disable - stops execution
* mem - displays the first 100 or so words of data memory
* regs - shows the contents of all 32 registers
* step - steps the program counter and shows the step from/to value.
* init - used by the other scripts (severely needs to be removed. slows things way down)

###### PASM Debug Files

To make any sense of the program counter, you'll need to generate a list file by passing "-l" (as in little) to [pasm](https://github.com/beagleboard/am335x_pru_package/tree/master/pru_sw/utils), when compiling the pru source code. This will generate a <source>.lst file with the asm source for each value of the program counter, that will look something like:

    jtag_pru.p(  393) : 0x0009 = 0xe1003393 :     SBBO     r19, r19, 0x00, 4
    jtag_pru.p(  394) : 0x000a = 0x240001e0 :     mov      r0, 0x0001
    jtag_pru.p(  394) : 0x000b = 0xe1ff3380 :     SBBO     r0, r19, 0xFF, 4
    jtag_pru.p(  395) : 0x000c = 0xe10c3393 :     SBBO     r19, r19, 0x0C, 4
    jtag_pru.p(  406) : 0x000d = 0x240012e1 :     mov      r1, 18
    
