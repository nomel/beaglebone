PRU Debug Scripts
==========

Random debug scripts that use the horribly slow devmem2 program to read/modify pru memory.

###### Scripts

Scripts for the individual prus can be found in [pru0](pru0)and [pru1](pru1).

* reset - resets the pru.
* enable - enables execution of the current firmware.
* disable - stops execution
* mem - displays the first 100 or so words of data memory
* regs - shows the contents of all 32 registers
* step - steps the program counter and shows the step from/to value.
* init - used by the other scripts (severely needs to be removed. slows things way down)

###### PASM Debug Files

To make any sense of the program counter, you'll need to generate a list file by passing "-l" (as in little) to pasm, when compiling the pru source code. This will generate a <source>.lst file with the asm source for each value of the program counter.
